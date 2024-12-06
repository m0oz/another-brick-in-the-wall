export interface Brick {
  placed: boolean;
  width: number;
  stride: number | null;
}

export interface WallState {
  bricks: Brick[][];
  is_complete: boolean;
}

export interface Stride {
  origin_x: number;
  origin_y: number;
  width: number;
  height: number;
}

export interface InitializeRequest {
  width: number;
  height: number;
  mode: string;
  bond: string;
}
