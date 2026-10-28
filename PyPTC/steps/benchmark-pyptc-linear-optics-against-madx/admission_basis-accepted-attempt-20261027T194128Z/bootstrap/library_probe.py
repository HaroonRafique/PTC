import json,sys; sys.path.insert(0,sys.argv[1]); from pyptc import PTC; p=PTC(sys.argv[2]); print(json.dumps({'library':p.library.resolve().as_posix(),'api_level':p.api_level()}))
