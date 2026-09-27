import pytest

from retail_owl_shacl_poc.swrl_demo import SWRLDemoError, run_swrl_demo


def test_missing_java_compiler_is_reported_before_starting_maven(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "retail_owl_shacl_poc.swrl_demo.shutil.which",
        lambda name: None if name == "javac" else f"/fake/{name}",
    )
    monkeypatch.setattr(
        "retail_owl_shacl_poc.swrl_demo.subprocess.run",
        lambda *args, **kwargs: pytest.fail("Maven ne doit pas démarrer sans javac."),
    )

    with pytest.raises(SWRLDemoError, match="javac") as error:
        run_swrl_demo(tmp_path / "never-created.ttl")

    assert "La démo Python/SHACL reste utilisable sans eux." in str(error.value)
