"""Micro-mesure HTTP locale, sans navigateur ni temps des fonds externes."""
import json,threading,time,urllib.request,statistics
from functools import partial
from http.server import ThreadingHTTPServer
from national.serve import Handler
from national.collect import ROOT,dump,now
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')));threading.Thread(target=s.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(s.server_port);results=[]
for code in ['75056','17300','13004','37261','74056','23096','2A004','97411','31555']:
 times=[];n=0
 for i in range(5):
  t=time.perf_counter()
  with urllib.request.urlopen(base+'/api/v2/climate?code='+code+'&horizon=2050') as r:b=r.read();status=r.status
  times.append((time.perf_counter()-t)*1000);n=len(b)
 results.append({'code':code,'repetitions':5,'median_ms':round(statistics.median(times),2),'max_ms':round(max(times),2),'bytes':n,'status':status})
s.shutdown();s.server_close();dump(ROOT/'reports/performance_http.json',{'at':now(),'method':'HTTP boucle locale, 5 lectures consécutives par commune ; pas de navigateur, pas de temps de rendu ou de tuiles IGN','results':results})
print(json.dumps(results,ensure_ascii=False))
