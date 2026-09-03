#!/usr/bin/env node

import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const hydraRoot = process.env.HYDRA_SYNTH_ROOT
if (!hydraRoot) throw new Error('HYDRA_SYNTH_ROOT must point to hydra-synth-minimal/packages/synth')

const outputRoot = process.argv[2] ?? 'experiments/workflows/hydra-fun-control-2026-09-03'
const synth = await import(pathToFileURL(path.resolve(hydraRoot, 'dist/index.js')))
const naga = await import(pathToFileURL(path.resolve(hydraRoot, 'node_modules/web-naga/web_naga.js')))
const wasm = await readFile(path.resolve(hydraRoot, 'node_modules/web-naga/web_naga_bg.wasm'))
naga.initSync({ module: wasm })

const WIDTH = 768
const HEIGHT = 768
const FRAMES = 73
const FPS = 24
const SEED = 20260902
const SOURCE_VIDEO = 'Gen-4_5.gen-4_5 (5).mp4'
const PROMPT = 'One continuous accelerating camera flight through a dense southern temperate rainforest, rotating smoothly around the vertical axis while moving forward. Preserve the circular domemaster projection, black exterior, forest structure, spatial rhythm, and camera path. One uninterrupted shot, no cuts, no text, silent.'

const variants = [
  {
    id: 'hydra-canny-passthrough-quality20',
    question: 'Does the Hydra IMAGE handoff preserve the ordinary Canny carrier closely enough to be operationally transparent?',
    code: 'src(s0).out(o0); render(o0)'
  },
  {
    id: 'hydra-canny-affine-quality20',
    question: 'Does H3 Fun Control follow a deliberately warped Canny trajectory when the warp is authored before native control encoding?',
    code: `src(s0)
  .scale(({ time }) => 1.0 + 0.08 * Math.sin(time * 2.0), 1, 1)
  .rotate(({ time }) => 0.08 * Math.sin(time * 1.5))
  .out(o0)

render(o0)`
  }
]

const compileInputs = async (code) => {
  const plan = await synth.compileTrustedHydraProgram({
    code,
    width: WIDTH,
    height: HEIGHT,
    frameCount: FRAMES,
    fps: FPS,
    startTime: 0,
    bpm: 60,
    seed: SEED,
    naga
  })
  return {
    code,
    width: WIDTH,
    height: HEIGHT,
    frame_count: FRAMES,
    fps: FPS,
    start_time: 0,
    bpm: 60,
    seed: SEED,
    compiled_plan: JSON.stringify(plan)
  }
}

const graphFor = async (variant) => {
  const prefix = `experiments/2026-09-03/hydra-fun-control/${variant.id}`
  return {
    '1': { class_type: 'CLIPLoader', inputs: { clip_name: 'qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors', type: 'minimax', device: 'default' } },
    '2': { class_type: 'VAELoader', inputs: { vae_name: 'minimax_h3_video_vae_fp16.safetensors' } },
    '3': { class_type: 'UNETLoader', inputs: { unet_name: 'minimax_h3_fl2va_pruned_int8_convrot.safetensors', weight_dtype: 'default' } },
    '4': { class_type: 'ModelPatchLoader', inputs: { name: 'minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors' } },
    '5': { class_type: 'LoadVideo', inputs: { file: SOURCE_VIDEO } },
    '6': { class_type: 'VideoTemporalCrop', inputs: { video: ['5', 0], start_frame: 0, length: FRAMES } },
    '7': { class_type: 'GetVideoComponents', inputs: { video: ['6', 0] } },
    '8': { class_type: 'ImageScale', inputs: { image: ['7', 0], upscale_method: 'lanczos', width: WIDTH, height: HEIGHT, crop: 'center' } },
    '9': { class_type: 'ImageFromBatch', inputs: { image: ['8', 0], batch_index: 0, length: 1 } },
    '10': { class_type: 'Canny', inputs: { image: ['8', 0], low_threshold: 0.2, high_threshold: 0.5 } },
    '11': { class_type: 'HydraRenderSequence', inputs: { ...await compileInputs(variant.code), s0: ['10', 0] } },
    '12': { class_type: 'MiniMaxH3ImageToVideo', inputs: { clip: ['1', 0], vae: ['2', 0], prompt: PROMPT, width: WIDTH, height: HEIGHT, length: FRAMES, first_frame: ['9', 0] } },
    '13': { class_type: 'MiniMaxH3FunControlNetApply', inputs: { model: ['3', 0], model_patch: ['4', 0], vae: ['2', 0], strength: 1.0, start_percent: 0.0, end_percent: 1.0, control_video: ['11', 0] } },
    '14': { class_type: 'RandomNoise', inputs: { noise_seed: SEED } },
    '15': { class_type: 'BasicGuider', inputs: { model: ['13', 0], conditioning: ['12', 0] } },
    '16': { class_type: 'BasicScheduler', inputs: { model: ['13', 0], scheduler: 'simple', steps: 20, denoise: 1.0 } },
    '17': { class_type: 'KSamplerSelect', inputs: { sampler_name: 'res_multistep' } },
    '18': { class_type: 'SamplerCustomAdvanced', inputs: { noise: ['14', 0], guider: ['15', 0], sampler: ['17', 0], sigmas: ['16', 0], latent_image: ['12', 1] } },
    '19': { class_type: 'VAEDecode', inputs: { samples: ['18', 1], vae: ['2', 0] } },
    '20': { class_type: 'CreateVideo', inputs: { images: ['19', 0], fps: FPS } },
    '21': { class_type: 'SaveVideo', inputs: { video: ['20', 0], filename_prefix: `${prefix}/generated`, format: 'auto' } },
    '22': { class_type: 'CreateVideo', inputs: { images: ['10', 0], fps: FPS } },
    '23': { class_type: 'SaveVideo', inputs: { video: ['22', 0], filename_prefix: `${prefix}/canny_direct`, format: 'auto' } },
    '24': { class_type: 'CreateVideo', inputs: { images: ['11', 0], fps: FPS } },
    '25': { class_type: 'SaveVideo', inputs: { video: ['24', 0], filename_prefix: `${prefix}/canny_after_hydra`, format: 'auto' } }
  }
}

const writeJson = async (filename, value) => {
  await writeFile(path.join(outputRoot, filename), `${JSON.stringify(value, null, 2)}\n`, {
    encoding: 'utf8',
    flag: 'wx'
  })
}

await mkdir(path.join(outputRoot, 'graphs'), { recursive: true })
for (const variant of variants) {
  await writeJson(path.join('graphs', `${variant.id}.api.json`), await graphFor(variant))
}
await writeJson('batch-plan.json', {
  schema: 'comfy.run-batch/1',
  id: 'inside-valdivia-hydra-fun-control-20260903',
  steps: variants.map(({ id }) => ({
    id,
    graph: `graphs/${id}.api.json`,
    operation_ref: 'operation-ref.json'
  }))
})
await writeJson('matrix.json', {
  schema: 'inside-valdivia.hydra-fun-control-matrix/1',
  status: 'planned',
  held_constant: {
    source_video: SOURCE_VIDEO,
    source_window: [0, FRAMES],
    dimensions: [WIDTH, HEIGHT],
    fps: FPS,
    seed: SEED,
    prompt: PROMPT,
    model: 'minimax_h3_fl2va_pruned_int8_convrot.safetensors',
    control_patch: 'minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors',
    control_kind: 'Canny(0.2, 0.5)',
    sampler: 'res_multistep',
    scheduler: 'simple',
    steps: 20
  },
  prior_baseline: 'workflows/evaluations/2026-09-02/fun-control-canny-quality20.api.json',
  variants: variants.map(({ id, question, code }) => ({ id, question, hydra_code: code }))
})
