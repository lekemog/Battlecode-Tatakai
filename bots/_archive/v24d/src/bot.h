#include <string>
#pragma once
#include <cambc.h>
#include <array>
#include <cstdint>
#include <vector>

// Polaris V7: a main pack plus squads that split once strong enough, scheduled on camp respawns.
// leader, kills it together, one champion captures, gems are banked quickly,
// and gold is turned into Power stacks of the champion's best scaling stat.
class Bot {
    struct Group {
        cambc::map::camp_group handle;
        cambc::bitboard spawns;
        std::vector<cambc::vec2> probes;   // camp positions: cheap distance samples
        cambc::vec2 center{0,0};
        double hp=0,str=0;
        int gems=0,gold=0,respawn=50;
        bool monolith=false;
        int home_d=0,enemy_d=0,altar_d=0;   // static travel estimates
        unsigned ready_round=0;               // known respawn completion
        bool reward=false,alive_seen=false;
        unsigned seen_round=0;
        int sector=-1,elks=0;
    };
    struct Enemy {
        cambc::champion handle;
        cambc::vec2 pos;
        float hp,maxhp,strength;
        int range,gems;
        bool channel;
        cambc::champion_type type=cambc::champion_type::ryth;
        bool stunned=false;
        float focus=0;
    };
    struct Monster {
        cambc::camp handle;
        cambc::vec2 pos;
        float hp,strength;
        int group;
        bool awake;
    };

    bool initialized=false;
    int init_phase=0;unsigned init_next=0;
    std::vector<cambc::map::camp_group> pending_groups;
    cambc::bitboard enemy_base;
    int slot=0,team_size=1;
    unsigned round=0,last_log=0;
    int objective=-1;
    bool focus_build=false,frontline=false;
    std::vector<Group> groups;
    std::vector<cambc::champion> roster,enemy_roster;
    std::vector<Enemy> enemies;
    std::vector<Monster> monsters;
    std::vector<cambc::champion> allies;
    std::array<std::uint8_t,8> shared{};
    cambc::bitboard terrain,occupied,visible,altar_goals,all_spawns;
    cambc::distance_field altar_distance,home_distance,enemy_distance;
    std::vector<std::pair<cambc::vec2,unsigned>> deaths;
    cambc::vec2 last_pos{-1,-1};
    bool was_alive=true;
    int stalled=0;
    unsigned last_gems=0;
    int capturing=-1;
    unsigned last_choose=0,solo_choose=0;
    // Team plan (computed identically by every champion from the roster and the map).
    int role=0;                       // 0 = gem squad, 1 = gold farmer
    int squad=0;                      // which gem squad this champion belongs to
    int squads=1;unsigned ward_next=0;int herd_group=-2;bool herd_warded=false;int herd_try_since=-1;int escort_rounds=0;unsigned escort_block_until=0;int siege_started=-1;unsigned siege_cooldown=0;int siege_wait_since=-1,capture_since=-1,capture_group=-1;std::vector<unsigned> ban_until;void ban(int g,int rounds);bool banned(unsigned g) const;int bag_since=-1,staged_since=-1,contested_altars=-1,bank_alone_since=-1;
    std::vector<int> squad_members;   // roster slots in my squad
    std::vector<int> all_squads[3];
    std::vector<int> team_pool;
    bool enemy_has_cassi=false,enemy_aggressive_comp=false;
    int enemy_stuns=0;
    // Opponent model: shared aggression estimate (byte 6) built from evidence of invasion.
    double my_evidence=0;bool defensive=false;int aggression=0;
    float prev_hp=-1;unsigned last_enemy_round=0;std::uint8_t last_threat_cell=0;unsigned threat_cell_round=0;
    unsigned last_score=0,last_score_round=0;
    std::array<bool,8> prev_alive{true,true,true,true,true,true,true,true};std::vector<unsigned> team_deaths;
    std::array<int,82> s_ours{},s_theirs{};int s_last=-1;
    std::string tr_last_a;int tr_last_t=-9;unsigned tr_last_r=0;double tr_ratio=0;bool convoy_recalled=false;int rally_since=-1;bool raid=false,raid_failed=false;int raid_deaths0=0,max_aggr=0;int mode=0,mode_pending=0,mode_votes=0;unsigned mode_since=0,last_enemy_gain_round=0;int last_enemy_score=0;
    double kills_rate=0,pace_gap=0,my_danger=0;
    void update_profile();
    double danger_at(cambc::vec2 p,int carry) const;
    int threat_x=-1,threat_y=-1;
    bool threat_fresh=false;

    std::vector<cambc::vec2> altar_pos;std::vector<unsigned> altar_seen;
    std::vector<bool> altar_contested;std::vector<cambc::bitboard> altar_disk;
    int bank_wait=0,tribute_cancels=0;
    void init();
    void observe();
    void shop();
    double focus_w() const;
    double dps() const;
    double threat(cambc::vec2 p) const;
    bool move_to(cambc::bitboard goals,bool flee=false);
    bool combat(int group,bool players);
    int choose_group(cambc::vec2 from,double pack_dps,double pack_hp,std::array<int,3> exclude={-1,-1,-1},double tank_hp=1e9);
    bool merged() const;
    void update_split();
    double group_dps(const std::vector<int>& members,double& hp,double& tank) const;
    double farmable_share(const std::vector<int>& members,bool lenient) const;
    std::array<std::array<double,3>,8> ally_stats{};
    bool split_ok=false,stats_ready=false;
    mutable std::array<unsigned,8> alive_round{};mutable std::array<bool,8> alive_val{};
    bool ally_alive(int k) const;unsigned split_checked=0;
    int active_squad() const;
    const std::vector<int>& active_members() const;
    int leader_target();
    int squad_leader() const;
    void plan_team();
    int solo_target();
    bool guarded_siege=false;
    int idle_since=-1;
    bool cg_far=false;
    int bank_fail=0,bank_block_idx=-1;unsigned bank_block_until=0;
    bool pack_mode=true;
    int siege_group=-1;
    bool bank();
    bool handle_enemies();
    void write_byte(int index,std::uint8_t value);
    void log(const char* action,int target=-1);
public:
    void play_turn();
};
