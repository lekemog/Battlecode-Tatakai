// Polaris maprobe: test utility, not a competitor. Drafts any champions and prints one MAPINFO line (map size, camp-group totals, altars, walls, camp kinds) on its first game turn.
#include <cambc.h>
#include <cstdio>
#include <algorithm>
using namespace cambc;
int main(){
  static bool done=false;
  while(true){
    try{
      if(is_draft()){
        auto chosen=draft::current_draft(team::ally);
        for(int i=0;i<11;i++){auto p=(champion_draft)i; if(std::find(chosen.begin(),chosen.end(),p)==chosen.end()){draft::pick(p);break;}}
      } else if(!done){
        done=true;
        if(self().champion_name()==champion_type::ryth || true){
          unsigned G=0,Ge=0,ng=0; int nc[8]={0};
          for(auto& g: map::camp_groups()){ G+=g.gold_value(); Ge+=g.gem_value(); ++ng; for(auto&c:g) ++nc[(int)c.kind()]; }
          printf("MAPINFO %dx%d groups=%u gold=%u gems=%u altars=%d walls=%d wolf=%d elk=%d gemcl=%d goldcl=%d mono=%d golem=%d\n",map::width(),map::height(),ng,G,Ge,(int)map::altars().count(),(int)map::walls().count(),nc[0],nc[1],nc[2],nc[3],nc[4],nc[5]);
          fflush(stdout);
        }
      }
    }catch(std::exception&e){printf("MAPINFO err %s\n",e.what());fflush(stdout);}
    end_turn();
  }
}
