.PHONY: test acquire inventory cohort coverage overlap power gates figures clean
test:      ; python3 -m pytest tests/ -q
acquire:   ; ./run_phase1.sh
power:     ; python3 src/power_sim.py --reps 4000
calres:    ; python3 src/calibration_resolution.py
gates:     ; python3 src/gate_reproduction.py clone
figures:   ; @echo "figures regenerate from results/ only — no figure may read data_raw/"
