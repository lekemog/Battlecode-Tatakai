#include "policy_drafts.hpp"
#include <cassert>
using namespace field_study;
int main() {
    LandingTarget victim{500, 120, 30, 1, true, false, 1};
    Landing a{1, true, 1000, 20, 10, 0, 2, std::span(&victim, 1)};
    assert(landing_value(a) == 120); // 120 damage + one extra stun turn - 30 cost
    victim.existing_stun_turns = 2;
    assert(landing_value(a) == 90); // no overlapping-stun credit
    a.engine_legal = false;
    assert(!landing_value(a));
    a.engine_legal = true; a.incoming_after_landing = 1000;
    assert(!landing_value(a)); // no voluntary lethal landing in this initial policy
    std::array<Delivery, 3> d{{{33, 8, true, true}, {64, 16, true, true}, {99, 4, true, false}}};
    auto p = earliest_finish(947, 1000, d);
    assert(p && p->carriers == 2 && p->turns == 16);
    d[1].jointly_feasible = false;
    assert(!earliest_finish(947, 1000, d)); // unsafe or unavailable value cannot finish
    assert(earliest_finish(1000, 1000, d)->carriers == 0);
}
