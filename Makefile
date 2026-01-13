test:
	python conformance/signal_drift_lint.py witness.json export_bundle.json
	python conformance/release_controls_check.py export_bundle.json
	python conformance/wit_sbt_decl_check.py wit_contract_meta.json
	python conformance/cdm_record_lint.py cdm_example_record.json
	python conformance/cdm_ledger_validator.py cdm_records_sample
