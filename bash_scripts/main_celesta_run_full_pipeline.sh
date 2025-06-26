#!/bin/bash
cd ../

# enter samples to run in parallel
samples=(
  "10103"
  "28873"
  "34933"
  "49411"
  "39367"
  "08153"
  "09002"
  "02433"
  "07688"
  "00438"
  "04738"
  "07291"
  "00862"
  "10285"
)

# scripts to run sequentially per sample
scripts=(
  "celesta_create_obj"
  "celesta_plot_exp_prob"
  "celesta_assign_cells"
  "celesta_plot_results"
  "celesta_plot_interactive_assignments"
)

# enter path to log directory
logdir="/gpfs/data/proteomics/home/yb2612/results/logs"
mkdir -p "$logdir"

# run all samples in parallel
for sample in "${samples[@]}"; do
  echo "Submitting jobs for sample: $sample"

  previous_jobid=""

  # run all scripts sequentially per sample
  for script in "${scripts[@]}"; do
    job_name="${sample}_${script}"
    out_log="${logdir}/${job_name}_%j.out"
    err_log="${logdir}/${job_name}_%j.err"

    if [ -z "$previous_jobid" ]; then
      # no dependency for first job
      jobid=$(sbatch --job-name="$job_name" \
                     --output="$out_log" \
                     --error="$err_log" \
                     "${script}.sh" "$sample" | awk '{print $4}')
    else
      # subsequent jobs depend on the previous one finishing successfully
      jobid=$(sbatch --job-name="$job_name" \
                     --output="$out_log" \
                     --error="$err_log" \
                     --dependency=afterok:"$previous_jobid" \
                     "${script}.sh" "$sample" | awk '{print $4}')
    fi

    echo "  Submitted $script for $sample as job ID $jobid"
    previous_jobid="$jobid"
  done
done