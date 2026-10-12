import { TICK_SECONDS } from './types';

/** Converts variable render-frame time into bounded, fixed simulation ticks. */
export class FixedClock {
  readonly tickSeconds: number;
  readonly maxCatchUpSteps: number;
  private accumulator = 0;
  private paused = false;

  constructor(options: { tickSeconds?: number; maxCatchUpSteps?: number } = {}) {
    this.tickSeconds = options.tickSeconds ?? TICK_SECONDS;
    this.maxCatchUpSteps = options.maxCatchUpSteps ?? 5;
    if (!Number.isFinite(this.tickSeconds) || this.tickSeconds <= 0) throw new RangeError('tickSeconds must be positive');
    if (!Number.isInteger(this.maxCatchUpSteps) || this.maxCatchUpSteps < 1) throw new RangeError('maxCatchUpSteps must be a positive integer');
  }

  get isPaused(): boolean { return this.paused; }
  get interpolationAlpha(): number { return this.accumulator / this.tickSeconds; }
  pause(): void { this.paused = true; }
  resume(): void { this.paused = false; }

  /** Runs callback(tickSeconds) once per simulation tick and returns steps run. */
  advance(seconds: number, callback: (tickSeconds: number) => void): number {
    if (!Number.isFinite(seconds) || seconds < 0) throw new RangeError('seconds must be finite and non-negative');
    if (this.paused || seconds === 0) return 0;
    this.accumulator += seconds;
    let steps = 0;
    const tolerance = this.tickSeconds * 1e-10;
    while (this.accumulator + tolerance >= this.tickSeconds && steps < this.maxCatchUpSteps) {
      this.accumulator = Math.max(0, this.accumulator - this.tickSeconds);
      callback(this.tickSeconds);
      steps++;
    }
    // Drop excess whole ticks after a stall, retaining only the interpolation remainder.
    if (steps === this.maxCatchUpSteps && this.accumulator >= this.tickSeconds) this.accumulator %= this.tickSeconds;
    if (this.accumulator < tolerance) this.accumulator = 0;
    return steps;
  }

  reset(): void { this.accumulator = 0; this.paused = false; }
}
