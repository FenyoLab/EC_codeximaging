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

# enter name of script to run (no .sh extension)
script_name="celesta_assign_cells"

# enter path to log directory
logdir="../logs/"
mkdir -p "$logdir"

for sample in "${samples[@]}"; do
  echo "Submitting job for sample: $sample"
  sbatch --job-name="${sample}_${script_name}" \
         --output="${logdir}/%x_%j.out" \
         --error="${logdir}/%x_%j.err" \
         "${script_name}.sh" "$sample"
done