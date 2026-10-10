import unittest,time,json,io
from national.collect import ROOT,dump,now
from tests.test_france import FranceTests
s=io.StringIO();t=time.monotonic();suite=unittest.defaultTestLoader.loadTestsFromTestCase(FranceTests);r=unittest.TextTestRunner(stream=s,verbosity=2).run(suite)
dump(ROOT/'reports/france_tests.json',{'executed_at':now(),'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'seconds':round(time.monotonic()-t,3),'details':s.getvalue(),'browser':'Non réalisé : contrôle navigateur indisponible dans la session de reprise.','mobile':'CSS responsive présent ; vérification visuelle et clavier non réalisée.'});print(s.getvalue());raise SystemExit(not r.wasSuccessful())
