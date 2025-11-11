# Terrain Generator

Realistic procedural terrain generation for fantasy worlds. Generates elevation, moisture, rivers, and biomes at any scale from regional (50x50) to continental (200x200+).

## Installation

```bash
# Copy terraingen.py to your project
# No dependencies required - uses built-in Python only
```

## Library Usage

### Basic Generation

```python
from terraingen import TerrainGenerator

# Generate 80x60 terrain with seed
gen = TerrainGenerator(width=80, height=60, seed=12345)
terrain = gen.generate()

# Access terrain data
print(f"Rivers: {len(terrain['rivers'])}")
print(f"Average elevation: {gen.get_average_elevation():.3f}")

# Get specific tile
tile = terrain['tiles'][0]  # First tile
print(f"Tile at ({tile['x']}, {tile['y']}): {tile['biome']}, elev={tile['elevation']:.2f}")
```

### Advanced Configuration

```python
gen = TerrainGenerator(
    width=120,
    height=80,
    seed=42,
    mode='continent',         # or 'archipelago', 'highlands', 'none'
    octaves=6,                # More octaves = more detail
    persistence=0.5,          # How much each octave contributes
    lacunarity=2.0,          # Frequency multiplier per octave
    scale=120.0,             # Larger = broader features
    river_count=15,          # Number of rivers to generate
    prevailing_wind='west'   # Affects rain shadows
)
terrain = gen.generate()
```

### Generation Modes

**Continent**: Single landmass with ocean around edges
```python
terrain = TerrainGenerator(width=100, height=80, mode='continent', seed=123).generate()
```

**Archipelago**: Multiple islands scattered across map
```python
terrain = TerrainGenerator(width=100, height=80, mode='archipelago', seed=456).generate()
```

**Highlands**: Elevated terrain with valleys
```python
terrain = TerrainGenerator(width=100, height=80, mode='highlands', seed=789).generate()
```

**None**: Pure noise, no shaping applied
```python
terrain = TerrainGenerator(width=100, height=80, mode='none', seed=999).generate()
```

### Output Schema

```python
{
    'schema': 'terrain.v1',
    'seed': 12345,
    'width': 80,
    'height': 60,
    'mode': 'continent',
    'generation_params': {...},
    'tiles': [
        {
            'x': 0,
            'y': 0,
            'elevation': 0.65,    # 0.0-1.0
            'moisture': 0.42,     # 0.0-1.0
            'biome': 'grassland',
            'water': False,
            'river': False
        },
        ...
    ],
    'rivers': [
        {
            'id': 'river_001',
            'source': [45, 12],
            'mouth': [23, 45],
            'length': 67
        },
        ...
    ],
    'features': {
        'mountain_ranges': [],
        'lakes': []
    }
}
```

### Accessing Terrain Data

```python
# Get all land tiles
land_tiles = [t for t in terrain['tiles'] if not t['water']]

# Find mountains
mountains = [t for t in terrain['tiles'] if t['biome'] == 'mountain']

# Find river tiles
river_tiles = [t for t in terrain['tiles'] if t['river']]

# Get tile at specific coordinate
def get_tile(terrain, x, y):
    return next(t for t in terrain['tiles'] if t['x'] == x and t['y'] == y)

tile = get_tile(terrain, 40, 30)
```

### Biome Types

- **deep_ocean**: Elevation 0.0-0.3
- **ocean**: Elevation 0.3-0.38
- **beach**: Elevation 0.38-0.42
- **desert**: Elevation 0.42-0.7, Moisture 0.0-0.25
- **grassland**: Elevation 0.42-0.7, Moisture 0.25-0.6
- **temperate_forest**: Elevation 0.42-0.7, Moisture 0.6-1.0
- **wetlands**: Elevation 0.42-0.5, Moisture 0.7-1.0
- **highland**: Elevation 0.7-0.78
- **mountain**: Elevation 0.78-1.0

### Integration Example

```python
# Generate terrain for use in other generators
from terraingen import TerrainGenerator

# Create terrain
gen = TerrainGenerator(width=100, height=80, seed=12345)
terrain = gen.generate()

# Save for other tools
import json
with open('terrain.json', 'w') as f:
    json.dump(terrain, f, indent=2)

# Use in settlement placement (future tool)
# settlements = SettlementPlacer(seed=456).place(terrain)
```

## CLI Usage

### Quick Start

```bash
# Generate with defaults (80x60, random seed)
python terraingen.py --output terrain.json

# Specify size and seed
python terraingen.py --width 120 --height 100 --seed 42 --output terrain.json

# Preview with ASCII map
python terraingen.py --width 80 --height 60 --seed 12345 --output terrain.json --ascii
```

### CLI Options

```
--width INT          Map width (minimum 50) [default: 80]
--height INT         Map height (minimum 50) [default: 60]
--seed INT          Random seed for deterministic generation [default: random]
--mode STR          Generation mode: continent, archipelago, highlands, none [default: continent]
--octaves INT       Noise octaves (detail level) [default: 5]
--scale FLOAT       Noise scale (larger = broader features) [default: 100.0]
--rivers INT        Number of rivers to generate [default: 8]
--wind STR          Prevailing wind direction: west, east, north, south [default: west]
--output PATH       Output JSON file path [required]
--ascii             Print ASCII map preview
```

### CLI Examples

```bash
# Large continental map
python terraingen.py --width 150 --height 120 --mode continent --rivers 20 --output continent.json

# Island archipelago
python terraingen.py --width 100 --height 80 --mode archipelago --rivers 5 --output islands.json

# Highland terrain with more detail
python terraingen.py --width 100 --height 80 --mode highlands --octaves 6 --rivers 12 --output highlands.json

# Quick preview
python terraingen.py --width 60 --height 40 --seed 999 --ascii --output preview.json

# Different wind direction (affects rain shadows)
python terraingen.py --width 80 --height 60 --wind east --output wind_test.json
```

## Features

### Realistic Elevation
- Multi-octave Simplex noise for natural-looking terrain
- Domain warping for organic shapes
- Mode-specific shaping (continent falloff, island clusters, etc.)
- Full elevation range from ocean depths to mountain peaks

### River Generation
- Rivers flow downhill from high elevations to ocean
- Pathfinding traces realistic courses
- Rivers marked on tiles for easy identification
- Configurable river count

### Smart Moisture System
- Distance from water (ocean + rivers)
- Elevation modifiers (orographic lift)
- Rain shadow effects from mountains
- Prevailing wind direction support

### Biome Assignment
- Elevation + moisture based
- 9 distinct biomes
- Smooth transitions between types
- Configurable rules (edit `_load_biome_rules()`)

### Multiple Scales
- Works from 50x50 (regional) to 200x200+ (continental)
- Noise parameters scale appropriately
- Consistent quality at any size

## Technical Details

### Minimum Map Size
**50x50 tiles minimum**. Smaller maps don't work well with noise-based generation - you get either no variation or pure noise garbage. For testing or small areas, use 50x50 as the absolute minimum.

### Deterministic Generation
All generation is deterministic when using the same seed and parameters. Same seed = same terrain every time.

```python
# These will generate identical terrain
terrain1 = TerrainGenerator(width=80, height=60, seed=12345).generate()
terrain2 = TerrainGenerator(width=80, height=60, seed=12345).generate()
assert terrain1 == terrain2  # True
```

### Performance
- 80x60 map: ~2-3 seconds
- 120x100 map: ~8-10 seconds
- 200x200 map: ~45-60 seconds

River generation scales with map size and river count.

### Algorithm Overview

1. **Multi-octave noise**: Generate base elevation with multiple noise layers
2. **Domain warping**: Apply distortion for organic shapes
3. **Mode shaping**: Apply continent/archipelago/highlands shaping
4. **River tracing**: Trace downhill paths from high elevations
5. **Moisture calculation**: Distance to water + elevation + rain shadows
6. **Biome assignment**: Map elevation/moisture to biome types

## Customization

### Custom Biome Rules

Edit `_load_biome_rules()` method to define your own biomes:

```python
def _load_biome_rules(self) -> Dict:
    return {
        'my_custom_biome': {
            'elevation': [0.5, 0.7],
            'moisture': [0.4, 0.8]
        },
        # ... more biomes
    }
```

### Custom Mode Shaping

Override `_apply_mode_shaping()` to create custom terrain shapes:

```python
def _apply_mode_shaping(self, x: int, y: int, elevation: float) -> float:
    if self.mode == 'my_custom_mode':
        # Custom shaping logic here
        return modified_elevation
    return elevation
```

## Limitations

- Rivers don't combine/branch (each river is independent)
- No erosion simulation (just elevation + moisture)
- No plate tectonics (pure noise-based)
- Rain shadows are simplified (just checks upwind)
- Lakes are not explicitly generated (happen naturally in depressions)

These limitations keep the generator fast and simple while still producing realistic-looking terrain.

## Integration with Week 2 Pipeline

This terrain generator is Day 9 of the Week 2 RPG World Generator series. The output JSON feeds into:

- **Day 10**: Realm Painter (political boundaries)
- **Day 11**: Settlement Placer (cities, towns, forts)
- **Day 12**: History Generator (events, wars, ruins)

Example integration:

```python
from terraingen import TerrainGenerator
# from realmgen import RealmPainter  # Future
# from settlementgen import SettlementPlacer  # Future

# Generate terrain
terrain = TerrainGenerator(width=100, height=80, seed=123).generate()

# Paint realms (Day 10)
# realms = RealmPainter(seed=456).paint(terrain)

# Place settlements (Day 11)
# settlements = SettlementPlacer(seed=789).place(realms)
```

## License

MIT License - use however you want.

## Part of 30-for-30 Challenge

Day 9 of building 30 developer tools in 30 days. Week 2 focus: Procedural Generation Toolkit for tabletop RPGs.
Check out the [blog post(#https://jdookeran.medium.com/day-9-building-a-realistic-terrain-generator-69494320df0b)] where I dive into
