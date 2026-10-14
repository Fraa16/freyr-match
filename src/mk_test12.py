"""levels12test.json: levels 61-64 swapped for the mechanic test boards used by test_new12.py"""
import json
F = '........'
LV = json.load(open('levels12.json'))
LV[60] = {'name': 'Test Geschenke', 'moves': 30, 'target': 1000, 'board': [F, '.p....p.', '..C..C..', F, F, '..C..C..', '.p....p.', F]}
LV[61] = {'name': 'Test Gurken', 'moves': 30, 'target': 1000, 'board': [F, '.u....u.', F, F, F, F, '.u....u.', F]}
LV[62] = {'name': 'Test Wecker', 'moves': 30, 'target': 1000, 'clock': 9, 'collect': [[0, 99]], 'board': [F, F, '..a..a..', F, F, F, F, F]}
LV[63] = {'name': 'Test Turbo', 'moves': 30, 'target': 1000, 'boss': 30, 'turbo': 1, 'make': [['cat', 2], ['combo', 1]], 'goldrush': 5,
          'board': [F, F, F, '...VV...', '...VV...', F, F, F]}
json.dump(LV, open('levels12test.json', 'w'), ensure_ascii=False, indent=1)
print('ok')
