import json, math, sys
sys.path.insert(0, sys.argv[1])
from pyptc import PTC, read_flatfile_fibres
trace=[]
def call(name, fn, *args):
    value=fn(*args)
    trace.append({"call":name,"arguments":[str(x) for x in args],"return":value})
    return value
p=PTC(sys.argv[2]); call("PTC.init_lattice",p.init_lattice,sys.argv[3]); structure=call("PTC.machine_summary",p.machine_summary); fibres=read_flatfile_fibres(sys.argv[3]); trace.append({"call":"read_flatfile_fibres","arguments":[sys.argv[3]],"return_count":len(fibres)});
scalars={n:call("PTC.scalar:"+s,p.scalar,s) for n,s in {"p0c_gev_c":"ptc_get_p0c_","beta0":"ptc_get_beta0_","kinetic_gev":"ptc_get_kinetic_"}.items()};
initial=[0.0]*6; coords,loss=call("PTC.track_particle_ptc_with_loss",p.track_particle_ptc_with_loss,initial,1); print(json.dumps({"library":str(p.library.resolve()),"api_level":p.api_level(),"structure":structure,"fibre_count":len(fibres),"scalars":scalars,"initial":initial,"final":[float(x) for x in coords],"loss":loss,"finite":all(math.isfinite(float(x)) for x in coords),"executed_api_trace":trace},default=str))
