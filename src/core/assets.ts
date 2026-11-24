import type { AssetId } from './types.js';

export interface AssetRecord {
  readonly asset_id: AssetId | '';
  readonly kind: 'character' | 'scene_layer' | 'ui' | 'preview';
  readonly character: string;
  readonly scene: string;
  readonly expression: string;
  readonly layer: string;
  readonly file_relpath: string;
  readonly width: number;
  readonly height: number;
  readonly has_alpha: boolean;
  readonly foot_anchor_x?: number;
  readonly foot_anchor_y?: number;
  readonly status: 'example' | 'draft' | 'measured' | 'verified';
  readonly notes: string;
}

export type AssetState<T> =
  | { readonly status: 'missing' }
  | { readonly status: 'idle' | 'loading'; readonly record: AssetRecord }
  | { readonly status: 'ready'; readonly record: AssetRecord; readonly value: T }
  | { readonly status: 'error'; readonly record: AssetRecord; readonly message: string };

export function createAssetLoader<T>(
  records: readonly AssetRecord[],
  decode: (path: string, record: AssetRecord) => Promise<T>,
) {
  const states = new Map<AssetId, AssetState<T>>();
  const active = new Map<AssetId, Promise<AssetState<T>>>();

  for (const record of records) {
    if (record.kind === 'preview' || record.status !== 'verified') continue;
    if (!record.asset_id || states.has(record.asset_id)) {
      throw new Error('运行资源 ID 为空或重复：' + record.asset_id);
    }
    if (!/^(?:[a-z0-9_]+\/)+[a-z0-9_]+\.png$/.test(record.file_relpath)) {
      throw new Error('运行资源需要合规的库内相对路径：' + record.file_relpath);
    }
    states.set(record.asset_id, { status: 'idle', record });
  }

  function get(id: AssetId): AssetState<T> {
    return states.get(id) ?? { status: 'missing' };
  }

  function load(id: AssetId): Promise<AssetState<T>> {
    const current = get(id);
    if (current.status === 'ready' || current.status === 'missing') return Promise.resolve(current);
    const started = active.get(id);
    if (started) return started;

    const { record } = current;
    states.set(id, { status: 'loading', record });
    const pending = Promise.resolve()
      .then(() => decode(record.file_relpath, record))
      .then<AssetState<T>, AssetState<T>>(
        (value) => ({ status: 'ready', record, value }),
        (error: unknown) => ({ status: 'error', record, message: error instanceof Error ? error.message : String(error) }),
      )
      .then((outcome) => {
        states.set(id, outcome);
        active.delete(id);
        return outcome;
      });
    active.set(id, pending);
    return pending;
  }

  return {
    get,
    load,
    loadAll: (ids: readonly AssetId[]) => Promise.all(ids.map(load)),
  };
}
