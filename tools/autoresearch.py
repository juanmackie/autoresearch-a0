import os

from helpers.tool import Tool, Response
from usr.plugins.autoresearch.helpers import state as state_mod


class AutoResearchTool(Tool):
    """
    Autonomous code optimization experiment loop.

    Actions:
      optimize  — start or continue an optimization loop
      dashboard — generate a summary markdown file
      history   — show all past runs
      validate  — check state integrity
      reset     — clear state and start fresh
      status    — quick overview of current experiment
    """

    async def execute(self, **kwargs) -> Response:
        action = self.args.get("action", "optimize")

        if action == "optimize":
            return self._optimize()
        if action == "dashboard":
            return self._dashboard()
        if action == "history":
            return self._history()
        if action == "validate":
            return self._validate()
        if action == "reset":
            return self._reset()
        if action == "status":
            return self._status()

        return Response(
            message=f"Unknown action: {action}. Valid actions: optimize, dashboard, history, validate, reset, status.",
            break_loop=False,
        )

    # ------------------------------------------------------------------ #
    #  Optimize — the main entry point
    # ------------------------------------------------------------------ #

    def _optimize(self) -> Response:
        target_file = self.args.get("file", "")
        metric = self.args.get("metric", "runtime")
        metric_unit = self.args.get("metric_unit", "s")
        best_direction = self.args.get("best_direction", "lower")
        max_runs = int(self.args.get("max_runs", str(state_mod.MAX_RUNS_DEFAULT)))
        benchmark_command = self.args.get("benchmark_command") or None
        benchmark_runs = int(self.args.get("benchmark_runs", str(state_mod.BENCHMARK_RUNS)))
        hypothesis = self.args.get("hypothesis", "")
        description = self.args.get("description", "")

        s = state_mod.load_state()

        # -- First run: initialize config ----------------------------------
        if not s["runs"]:
            if not target_file:
                return Response(
                    message="Missing required parameter: file. Provide the target source file to optimize.",
                    break_loop=False,
                )
            if not os.path.isfile(target_file):
                return Response(
                    message=f"Target file not found: {target_file}",
                    break_loop=False,
                )
            config = state_mod.init_config(
                target_file, metric, metric_unit, best_direction,
                max_runs, benchmark_runs, benchmark_command,
            )
            s["config"] = config
        elif not s["config"]:
            return Response(
                message="State file exists but has no config entry. Run 'reset' first.",
                break_loop=False,
            )

        config = s["config"]
        target_file = target_file or config.get("targetFile", "")
        metric = metric or config.get("metricName", "runtime")
        metric_unit = metric_unit or config.get("metricUnit", "s")
        best_direction = best_direction or config.get("bestDirection", "lower")
        max_runs = max_runs or config.get("maxRuns", state_mod.MAX_RUNS_DEFAULT)
        benchmark_runs = benchmark_runs or config.get("benchmarkRuns", state_mod.BENCHMARK_RUNS)
        benchmark_command = benchmark_command or config.get("benchmarkCommand")

        if not os.path.isfile(target_file):
            return Response(
                message=f"Target file not found: {target_file}",
                break_loop=False,
            )

        run_id = state_mod.get_run_count() + 1

        if run_id > max_runs:
            return Response(
                message=f"Maximum runs ({max_runs}) reached. Generate a dashboard or reset to continue.",
                break_loop=False,
            )

        # -- Read current source -------------------------------------------
        with open(target_file, "r", encoding="utf-8") as fh:
            source_before = fh.read()
        source_hash_before = state_mod.sha256(source_before)

        # -- Benchmark baseline --------------------------------------------
        baseline = state_mod.run_benchmark(target_file, benchmark_command, benchmark_runs)
        if baseline is None:
            return Response(
                message=f"Benchmark failed on {target_file}. Check the file and benchmark command.",
                break_loop=False,
            )

        # -- Post-edit call: evaluate --------------------------------------
        if hypothesis and description:
            return self._evaluate(
                config=config,
                run_id=run_id,
                target_file=target_file,
                source_before=source_before,
                source_hash_before=source_hash_before,
                baseline=baseline,
                metric=metric,
                metric_unit=metric_unit,
                best_direction=best_direction,
                benchmark_command=benchmark_command,
                benchmark_runs=benchmark_runs,
                hypothesis=hypothesis,
                description=description,
            )

        # -- Pre-edit: return guidance to the agent ------------------------
        prev = state_mod.summarize_runs()
        trend_metrics = [
            r["metric"] for r in s["runs"]
            if r.get("type") != "config" and r.get("metric") is not None
        ]
        trend_line = state_mod.sparkline(trend_metrics) if trend_metrics else ""

        msg = (
            f"## AutoResearch Run #{run_id}\n"
            f"- **Target:** `{target_file}`\n"
            f"- **Metric:** {metric} ({metric_unit}), best={best_direction}\n"
            f"- **Baseline:** {baseline:.6f}{metric_unit}\n"
        )
        if trend_line:
            msg += f"- **Trend:** `{trend_line}` ({len(trend_metrics)} runs)\n"
        msg += (
            f"\n### Previous runs\n{prev}\n"
            f"\n### Next steps\n"
            f"1. Read `{target_file}` and analyze it.\n"
            f"2. Propose an optimization hypothesis.\n"
            f"3. Edit the file with your change.\n"
            f"4. Call the tool again with hypothesis and description:\n"
            f"   `autoresearch` action=optimize file={target_file} "
            f"hypothesis=\"your hypothesis\" description=\"what you changed\"`\n"
        )

        return Response(message=msg, break_loop=False)

    # ------------------------------------------------------------------ #
    #  Evaluate — post-edit benchmark + keep/discard
    # ------------------------------------------------------------------ #

    def _evaluate(self, config, run_id, target_file, source_before,
                  source_hash_before, baseline, metric, metric_unit,
                  best_direction, benchmark_command, benchmark_runs,
                  hypothesis, description) -> Response:

        with open(target_file, "r", encoding="utf-8") as fh:
            source_after = fh.read()
        source_hash_after = state_mod.sha256(source_after)

        # No change
        if source_hash_before == source_hash_after:
            result = state_mod.build_result_entry(
                run_id=run_id, target_file=target_file,
                hypothesis=hypothesis, description=description,
                metric_before=baseline, metric_after=baseline,
                metric_unit=metric_unit, best_direction=best_direction,
                source_hash_before=source_hash_before,
                source_hash_after=source_hash_after,
                status="skip", notes="File was not modified.",
            )
            state_mod.append_state(result)
            return Response(
                message=f"Run #{run_id}: No changes detected in `{target_file}`. Edit the file first, then call optimize again.",
                break_loop=False,
            )

        # Benchmark modified source
        new_metric = state_mod.run_benchmark(target_file, benchmark_command, benchmark_runs)

        if new_metric is None:
            # Revert on failure
            with open(target_file, "w", encoding="utf-8") as fh:
                fh.write(source_before)
            result = state_mod.build_result_entry(
                run_id=run_id, target_file=target_file,
                hypothesis=hypothesis, description=description,
                metric_before=baseline, metric_after=None,
                metric_unit=metric_unit, best_direction=best_direction,
                source_hash_before=source_hash_before,
                source_hash_after=source_hash_after,
                status="error", notes="Benchmark failed — file reverted.",
            )
            state_mod.append_state(result)
            return Response(
                message=f"Run #{run_id}: Benchmark failed on modified source. File reverted.",
                break_loop=False,
            )

        # Evaluate
        improved = state_mod.is_improvement(baseline, new_metric, best_direction)
        status = "keep" if improved else "discard"
        delta = new_metric - baseline
        delta_pct = (delta / baseline * 100) if baseline != 0 else 0

        if status == "discard":
            with open(target_file, "w", encoding="utf-8") as fh:
                fh.write(source_before)

        # Log result
        result = state_mod.build_result_entry(
            run_id=run_id, target_file=target_file,
            hypothesis=hypothesis, description=description,
            metric_before=baseline, metric_after=new_metric,
            metric_unit=metric_unit, best_direction=best_direction,
            source_hash_before=source_hash_before,
            source_hash_after=source_hash_after,
            status=status,
        )
        state_mod.append_state(result)

        # Check convergence and max runs
        converged = state_mod.check_convergence()
        total_runs = state_mod.get_run_count()
        s = state_mod.load_state()
        best = state_mod.find_best_run(s["runs"])

        # Sparklines
        all_metrics = [
            r["metric"] for r in s["runs"]
            if r.get("type") != "config" and r.get("metric") is not None
        ]
        trend = state_mod.sparkline(all_metrics) if all_metrics else ""
        bar = ""
        bar_range = ""
        if all_metrics:
            bar_lo, bar_hi = min(all_metrics), max(all_metrics)
            bar = state_mod.horizontal_bar(new_metric, bar_lo, bar_hi)
            bar_range = f"{bar_lo:.4f} {bar} {bar_hi:.4f}"

        msg = (
            f"## AutoResearch Run #{run_id} Result\n"
            f"- **Status:** {status}\n"
            f"- **Before:** {baseline:.6f}{metric_unit}\n"
            f"- **After:** {new_metric:.6f}{metric_unit}\n"
            f"- **Delta:** {delta_pct:+.2f}%\n"
            f"- **Hypothesis:** {hypothesis}\n"
        )
        if trend:
            msg += f"- **Trend:** `{trend}` ({len(all_metrics)} runs)\n"
        if bar_range:
            msg += f"- **Range:** `{bar_range}`\n"
        if best:
            msg += (
                f"\n**Best so far:** Run #{best['run']} — "
                f"{best['metric']:.6f}{metric_unit} "
                f"({best.get('description', '')})\n"
            )
        if converged:
            msg += (
                "\n**Convergence detected:** Last 3 runs discarded. "
                "Consider generating a dashboard or trying a different approach.\n"
            )
        elif total_runs < config.get("maxRuns", state_mod.MAX_RUNS_DEFAULT):
            msg += (
                f"\nCall `autoresearch` action=optimize file={target_file} "
                f"to continue (run {total_runs + 1}/{config.get('maxRuns', state_mod.MAX_RUNS_DEFAULT)}).\n"
            )
        else:
            msg += "\n**Max runs reached.** Generate a dashboard to review results.\n"

        return Response(message=msg, break_loop=False)

    # ------------------------------------------------------------------ #
    #  Dashboard
    # ------------------------------------------------------------------ #

    def _dashboard(self) -> Response:
        content = state_mod.generate_dashboard()
        if content.startswith("No experiment"):
            return Response(message=content, break_loop=False)
        return Response(
            message=f"Dashboard written to `{state_mod.DASHBOARD_FILE}` and appended to `{state_mod.WORKLOG_FILE}`.\n\n{content[:2000]}",
            break_loop=False,
        )

    # ------------------------------------------------------------------ #
    #  History
    # ------------------------------------------------------------------ #

    def _history(self) -> Response:
        return Response(message=state_mod.format_history(), break_loop=False)

    # ------------------------------------------------------------------ #
    #  Validate
    # ------------------------------------------------------------------ #

    def _validate(self) -> Response:
        issues = state_mod.validate_state()
        if issues:
            return Response(
                message=f"Validation found {len(issues)} issue(s):\n" + "\n".join(f"- {i}" for i in issues),
                break_loop=False,
            )
        total = state_mod.get_run_count()
        return Response(message=f"State valid. {total} runs recorded.", break_loop=False)

    # ------------------------------------------------------------------ #
    #  Reset
    # ------------------------------------------------------------------ #

    def _reset(self) -> Response:
        backup = state_mod.reset_state()
        if backup:
            return Response(message=f"State reset. Backup saved to `{backup}`.", break_loop=False)
        return Response(message="No state file to reset.", break_loop=False)

    # ------------------------------------------------------------------ #
    #  Status
    # ------------------------------------------------------------------ #

    def _status(self) -> Response:
        s = state_mod.load_state()
        if not s["config"]:
            return Response(message="No active experiment. Call autoresearch action=optimize to start.", break_loop=False)

        config = s["config"]
        total = state_mod.get_run_count()
        best = state_mod.find_best_run(s["runs"])
        converged = state_mod.check_convergence()

        msg = (
            f"## AutoResearch Status\n"
            f"- **Target:** `{config.get('targetFile', '?')}`\n"
            f"- **Metric:** {config.get('metricName', '?')} ({config.get('metricUnit', '?')}), best={config.get('bestDirection', '?')}\n"
            f"- **Runs:** {total}/{config.get('maxRuns', '?')}\n"
        )
        if best:
            msg += f"- **Best:** Run #{best['run']} — {best['metric']:.6f}{config.get('metricUnit', '')}\n"
        if converged:
            msg += "- **Status:** Converged (last 3 runs discarded)\n"
        elif total >= config.get("maxRuns", state_mod.MAX_RUNS_DEFAULT):
            msg += "- **Status:** Max runs reached\n"
        else:
            msg += "- **Status:** Active\n"

        return Response(message=msg, break_loop=False)
