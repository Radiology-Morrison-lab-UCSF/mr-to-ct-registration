#!/bin/bash
# Run like so:
# bash /full-path-to/main_batch.sh 'full-path-to-your-data-containing-subjects'

SCRIPT_DIR=$(dirname $0)
dir_top=$1/
directoryCount=$(find $dir_top -mindepth 1 -maxdepth 1 -type d | wc -l)

noCPUs=8

sbatch <<EOT
#!/bin/bash
#SBATCH --array=0-$directoryCount
#SBATCH --time=00:59:59
#SBATCH --partition=short
#SBATCH --cpus-per-task=$noCPUs
#SBATCH --mem=16gb
#SBATCH --nodes=1
#SBATCH -D $dir_top

set -e

subjectDirectories=(*/)
dir_working=$dir_top\${subjectDirectories[\$SLURM_ARRAY_TASK_ID]}

loc_t1=\$dir_working/*T1w.nii.gz

echo $SCRIPT_DIR
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=$noCPUs
$SCRIPT_DIR/main.sh \$dir_working \$loc_t1
EOT