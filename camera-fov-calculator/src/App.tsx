import React, { useEffect, useMemo, useState } from 'react'
import './App.css'
import { useTranslation } from 'react-i18next'

type CmosKey = 'APS-C' | 'Full Frame' | 'M43' | '1/2.3in'

type Rect = { x: number; y: number; w: number; h: number }

interface ParameterSet {
  name: string
  cmos_type: CmosKey
  focal_length: number // mm
  distance: number // m
  object_height: number // m
  aspect_ratio: number // w/h
  color: string // hex
  rect?: Rect
}

const CMOS_SIZES: Record<CmosKey, { w: number; h: number }> = {
  'APS-C': { w: 0.0238, h: 0.0158 },
  'Full Frame': { w: 0.036, h: 0.024 },
  M43: { w: 0.0173, h: 0.013 },
  '1/2.3in': { w: 0.00617, h: 0.00455 },
}

const COLOR_PALETTE = [
  '#4285F4',
  '#EA4335',
  '#FBBC05',
  '#34A853',
  '#673AB7',
  '#FF5722',
  '#009688',
  '#9C27B0',
  '#2196F3',
  '#4CAF50',
  '#FF9800',
  '#E91E63',
]

const SENSOR_VIEW = { x: 50, y: 50, w: 200, h: (200 * 2) / 3 }
const SCENE_W = 300
const SCENE_H = 250

function calc_h_i(f_m: number, u_m: number, h_o_m: number) {
  // h_i = (h_o * f) / (u - f)
  return (h_o_m * f_m) / (u_m - f_m)
}

function calculateRectangle(ps: Omit<ParameterSet, 'rect'>): Rect {
  const cmos_w = CMOS_SIZES[ps.cmos_type].w // meters
  const f_m = ps.focal_length / 1000 // meters
  const u_m = ps.distance
  const h_o = ps.object_height

  const h_i = calc_h_i(f_m, u_m, h_o)
  const h_prop = h_i / cmos_w

  let img_w = SENSOR_VIEW.w * Math.min(h_prop, 1.0)
  let img_h = img_w / ps.aspect_ratio
  const sensor_h = SENSOR_VIEW.h
  if (img_h > sensor_h) {
    img_h = sensor_h
    img_w = img_h * ps.aspect_ratio
  }
  const x = SENSOR_VIEW.x + (SENSOR_VIEW.w - img_w) / 2
  const y = SENSOR_VIEW.y + (SENSOR_VIEW.h - img_h) / 2
  return { x, y, w: img_w, h: img_h }
}

function calculateFovDegrees(focalLengthMm: number, sensorSizeMm: number): number {
  const f = focalLengthMm
  const s = sensorSizeMm
  const fovRad = 2 * Math.atan(s / (2 * f))
  return (fovRad * 180) / Math.PI
}

function sensorCoveragePercent(rect?: Rect): number {
  if (!rect) return 0
  const sensorArea = SENSOR_VIEW.w * SENSOR_VIEW.h
  const rectArea = rect.w * rect.h
  return Math.min(100, (rectArea / sensorArea) * 100)
}

function App() {
  const { t, i18n } = useTranslation()
  const [parameterSets, setParameterSets] = useState<ParameterSet[]>([])
  const [selectedIndex, setSelectedIndex] = useState<number>(-1)

  // inputs
  const [cmos, setCmos] = useState<CmosKey>('APS-C')
  const [focal, setFocal] = useState<number>(50)
  const [distance, setDistance] = useState<number>(10.0)
  const [objHeight, setObjHeight] = useState<number>(0.5)
  const [aspect, setAspect] = useState<number>(1.0)
  const [colorIdx, setColorIdx] = useState<number>(0)
  const currentColor = useMemo(
    () => COLOR_PALETTE[colorIdx % COLOR_PALETTE.length],
    [colorIdx]
  )

  // set document title by i18n
  useEffect(() => {
    document.title = t('app.title')
  }, [t, i18n.language])

  function toggleLanguage() {
    const next = i18n.language?.toLowerCase().startsWith('zh') ? 'en' : 'zh'
    void i18n.changeLanguage(next)
  }

  function nextColor(): string {
    const col = COLOR_PALETTE[colorIdx % COLOR_PALETTE.length]
    setColorIdx((i: number) => i + 1)
    return col
  }

  function addParameterSet() {
    // default name: format-focal_length-index (lowercase with underscores for spaces)
    const cmosShort = cmos.toLowerCase().replace(/\s+/g, '_')
    const same = parameterSets.filter(
      (p: ParameterSet) =>
        p.cmos_type === cmos && Math.round(p.focal_length) === Math.round(focal)
    ).length
    const defaultName = `${cmosShort}-${Math.round(focal)}mm-${same + 1}`

    const base: Omit<ParameterSet, 'rect' | 'name' | 'color'> = {
      cmos_type: cmos,
      focal_length: focal,
      distance,
      object_height: objHeight,
      aspect_ratio: aspect,
    }

    const rect = calculateRectangle({ ...base, name: defaultName, color: currentColor })
    const ps: ParameterSet = {
      ...base,
      name: defaultName,
      color: nextColor(),
      rect,
    }
    setParameterSets((arr: ParameterSet[]) => [...arr, ps])
    setSelectedIndex(parameterSets.length)
  }

  function deleteSelected() {
    if (selectedIndex < 0 || selectedIndex >= parameterSets.length) return
    const next = parameterSets.slice()
    next.splice(selectedIndex, 1)
    setParameterSets(next)
    setSelectedIndex(-1)
  }

  const selected =
    selectedIndex >= 0 && selectedIndex < parameterSets.length
      ? parameterSets[selectedIndex]
      : undefined

  return (
    <div className="app">
      {/* Panel on the left */}
      <div className="panel">
        <div className="form" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontWeight: 600 }}>{t('app.title')}</div>
          <button title={i18n.language?.toLowerCase().startsWith('zh') ? t('actions.switchToEN') : t('actions.switchToZH')} onClick={toggleLanguage}>
            {t('actions.toggleLanguage')}
          </button>
        </div>
        <div className="form">
          <label>
            <span>{t('form.sensorType')}</span>
            <select
              value={cmos}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setCmos(e.target.value as CmosKey)
              }
            >
              {Object.keys(CMOS_SIZES).map((k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>{t('form.focalLength')}</span>
            <input
              type="number"
              min={1}
              max={1000}
              value={focal}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFocal(Number(e.target.value))
              }
            />
            <span className="suffix">{t('units.mm')}</span>
          </label>

          <label>
            <span>{t('form.objectDistance')}</span>
            <input
              type="number"
              min={0.1}
              max={1000}
              step={0.1}
              value={distance}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setDistance(Number(e.target.value))
              }
            />
            <span className="suffix">{t('units.m')}</span>
          </label>

          <label>
            <span>{t('form.objectHeight')}</span>
            <input
              type="number"
              min={0.01}
              max={1000}
              step={0.01}
              value={objHeight}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setObjHeight(Number(e.target.value))
              }
            />
            <span className="suffix">{t('units.m')}</span>
          </label>

          <label>
            <span>{t('form.aspectRatio')}</span>
            <input
              type="number"
              min={0.1}
              max={10}
              step={0.01}
              value={aspect}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setAspect(Number(e.target.value))
              }
            />
          </label>

          <button onClick={addParameterSet}>{t('actions.add')}</button>
        </div>

        <div className="list">
          <div className="list-title">{t('list.title')}</div>
          <ul>
            {parameterSets.map((ps: ParameterSet, idx: number) => (
              <li
                key={ps.name + idx}
                className={idx === selectedIndex ? 'selected' : ''}
                onClick={() => setSelectedIndex(idx)}
              >
                <span className="color" style={{ background: ps.color }} />
                {ps.name}
              </li>
            ))}
          </ul>
          <button disabled={selectedIndex < 0} onClick={deleteSelected}>
            {t('actions.deleteSelected')}
          </button>
        </div>

        <div className="details">
          <div className="group-title">{t('details.title')}</div>
          {selected ? (
            <>
              <div className="row">
                <span className="label">{t('details.name')}</span>
                <span className="value">{selected.name}</span>
              </div>
              <div className="row">
                <span className="label">{t('details.sensorType')}</span>
                <span className="value">
                  {selected.cmos_type} (
                  {(CMOS_SIZES[selected.cmos_type].w * 1000).toFixed(1)}mm x{' '}
                  {(CMOS_SIZES[selected.cmos_type].h * 1000).toFixed(1)}mm)
                </span>
              </div>
              <div className="row">
                <span className="label">{t('details.focalLength')}</span>
                <span className="value">{selected.focal_length.toFixed(1)} mm</span>
              </div>
              <div className="row">
                <span className="label">{t('details.objectDistance')}</span>
                <span className="value">{selected.distance.toFixed(2)} m</span>
              </div>
              <div className="row">
                <span className="label">{t('details.objectHeight')}</span>
                <span className="value">{selected.object_height.toFixed(2)} m</span>
              </div>
              <div className="row">
                <span className="label">{t('details.aspectRatio')}</span>
                <span className="value">{selected.aspect_ratio.toFixed(2)}</span>
              </div>
              <div className="row">
                <span className="label">{t('details.fov')}</span>
                <span className="value">
                  {t('format.fovH')} {calculateFovDegrees(selected.focal_length, CMOS_SIZES[selected.cmos_type].w * 1000).toFixed(1)}°
                  {'  '}{t('format.fovV')}{' '}
                  {calculateFovDegrees(selected.focal_length, CMOS_SIZES[selected.cmos_type].h * 1000).toFixed(1)}°
                </span>
              </div>
              <div className="row">
                <span className="label">{t('details.coverage')}</span>
                <span className="value">{sensorCoveragePercent(selected.rect).toFixed(1)}{t('format.coverageSuffix')}</span>
              </div>
            </>
          ) : (
            <div className="placeholder">{t('details.placeholder')}</div>
          )}
        </div>
      </div>

      {/* View on the right; SVG fills remaining space */}
      <div className="view">
        <svg
          width="100%"
          height="100%"
          viewBox={`0 0 ${SCENE_W} ${SCENE_H}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {/* background */}
          <rect x={0} y={0} width={SCENE_W} height={SCENE_H} fill="transparent" />
          {/* sensor frame */}
          <rect
            x={SENSOR_VIEW.x}
            y={SENSOR_VIEW.y}
            width={SENSOR_VIEW.w}
            height={SENSOR_VIEW.h}
            fill="none"
            stroke={"var(--sensor-stroke)"}
            strokeDasharray="4 4"
          />
          <text x={SENSOR_VIEW.x} y={SENSOR_VIEW.y - 6} fontSize={10} fill={"var(--sensor-stroke)"}>
            {t('svg.sensorArea')}
          </text>
          {/* rectangles */}
          {parameterSets.map((ps: ParameterSet, idx: number) =>
            ps.rect ? (
              <rect
                key={idx}
                x={ps.rect.x}
                y={ps.rect.y}
                width={ps.rect.w}
                height={ps.rect.h}
                fill="none"
                stroke={ps.color}
                strokeWidth={1.5}
              />
            ) : null
          )}
        </svg>
      </div>
    </div>
  )
}

export default App
