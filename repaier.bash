#!/bin/bash
param=$1
if [[ "$param" = "ubuntu" ]]; then
python << END
from settings.repair_tasks import rep
rep.ubuntu_path('tasks/mat_demo_task.txt')
rep.ubuntu_path('tasks/info_demo_task.txt')
END
echo "Done![now path for ubuntu]"
else
python << END
from settings.repair_tasks import rep
rep.windows_path('tasks/mat_demo_task.txt')
rep.windows_path('tasks/info_demo_task.txt')
END
echo "Done![now path for win]"
fi