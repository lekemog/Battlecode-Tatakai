"""add_profiler.py BOT_DIR : add the v51p profiler (prof.h + hooks) to a copy of any v50-line bot (v50h5e, v51a, v51b ...).
Behaviour-neutral apart from a few fuel units per fuel() read. Run profsweep.sh with the bot name afterwards (BOT env var)."""
import re, shutil, sys, os
d = sys.argv[1]
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'bots', 'v51p', 'src', 'prof.h')
shutil.copy(src, os.path.join(d, 'src', 'prof.h'))
c = open(os.path.join(d, 'src', 'config.h')).read()
if 'inline constexpr bool profile' not in c:
    c = c.replace('inline constexpr std::uint64_t fuel_phase_log = 25000;', 'inline constexpr std::uint64_t fuel_phase_log = 25000;\ninline constexpr bool profile = true;  // prof.h', 1)
open(os.path.join(d, 'src', 'config.h'), 'w').write(c)
p = os.path.join(d, 'src', 'brain.cpp'); s = open(p).read()
if 'prof::' in s: sys.exit('already profiled')
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a)
    s = s.replace(a, b, 1)
rep('#include "brain.h"', '#include "brain.h"\n#include "prof.h"')
rep('    FuelTrace trace;\n    trace.begin();', '    FuelTrace trace;\n    trace.begin();\n    prof::begin_turn();')
rep('    trace.mark("end");\n    if (fuel_ok(cfg::fuel_phase_log))', '    trace.mark("end");\n    prof::end_turn(trace, static_cast<int>(cambc::round_number()));\n    if (fuel_ok(cfg::fuel_phase_log))')
for name, call, cond in (('threats', 'handle_threats', 'fuel_phase_threats'), ('lowhp', 'handle_low_health', 'fuel_phase_basic'), ('tribute', 'handle_tribute', 'fuel_phase_basic'),
                         ('breach', 'handle_breach', 'fuel_phase_farm'), ('farm', 'handle_farm', 'fuel_phase_farm')):
    rep(f'!done && fuel_ok(cfg::{cond}) && (done = {call}(ctx, acts))', f'!done && prof::gate("{name}", fuel_ok(cfg::{cond})) && (done = {call}(ctx, acts))')
rep('const bool can_choose = fuel_ok(cfg::fuel_choose);', 'const bool can_choose = prof::gate("choose", fuel_ok(cfg::fuel_choose));')
rep('const bool can_compute = fuel_ok(world.field_cost() + 10000) && fuel_ok(cfg::fuel_light_farm);', 'const bool can_compute = prof::gate("field", fuel_ok(world.field_cost() + 10000) && fuel_ok(cfg::fuel_light_farm));')
rep('        ++time_use_[bucket];\n    }', '        ++time_use_[bucket];\n        prof::note(mode, why_, static_cast<int>(ctx.gems), ctx.hp_frac(), ctx.on_spawn, ctx.round, static_cast<int>(kit().type), cfg::tribute_gems, cfg::recall_health_frac);\n    }')
open(p, 'w').write(s)
print('profiler added to', d)
