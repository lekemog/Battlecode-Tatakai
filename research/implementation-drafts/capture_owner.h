#pragma once
#include <cmath>
#include <limits>
#include <span>

namespace polaris_draft {
// A validated, fresh owner lease is supplied by the caller's coordination protocol.
// This is NOT a new shared-memory wire format and reserves no existing bytes.
struct Lease { int group=-1, owner=-1, expires=-1; };
struct Capturer {
    int slot=-1;
    bool eligible=false;
    double arrival_rounds=0, opportunity_rounds=0;
};
inline int capture_owner(int group, int now, Lease current,
                         bool owner_proven_invalid, std::span<const Capturer> candidates) {
    // Absence from local vision is not proof of invalidity; honor a valid lease.
    if (!owner_proven_invalid && current.group==group && current.owner>=0
        && now<=current.expires) return current.owner;
    int best=-1;
    double cost=std::numeric_limits<double>::infinity();
    for (const auto& c : candidates) {
        if (!c.eligible || c.slot<0 || !std::isfinite(c.arrival_rounds)
            || !std::isfinite(c.opportunity_rounds)
            || c.arrival_rounds<0 || c.opportunity_rounds<0) continue;
        // Opportunity cost expressed as equivalent occupied champion-rounds.
        const double next=c.arrival_rounds+c.opportunity_rounds;
        if (next<cost || (next==cost && (best<0 || c.slot<best))) {
            best=c.slot; cost=next;
        }
    }
    return best;
}
// The non-owner still helps clear a LIVE group. Release applies only after the kill.
inline bool release_helper(bool reward_available, int owner, int self_slot,
                            bool explicit_shared_capture) {
    return reward_available && owner>=0 && owner!=self_slot && !explicit_shared_capture;
}
} // namespace polaris_draft
