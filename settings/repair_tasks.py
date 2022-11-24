class Repaier:
    def __init__(self) -> None:
        pass
    

    def ubuntu_path(self, path: str = 'tasks/mat_demo_task.txt'):
        try:
            f = open(path, 'r')
        except FileNotFoundError:
            path_update = input('Путь неверный\nВведи путь вручную: ')
            f = open(path_update, 'r')
            arr = f.readlines()
            for i in range(3, len(arr), 4):
                arr[i] = arr[i].replace('\\', '/')
            f.close()
            f = open(path_update, 'w')
            for i in arr:
                f.write(i)
            f.close()

        else:
            arr = f.readlines()
            for i in range(3, len(arr), 4):
                arr[i] = arr[i].replace('\\', '/')
            f.close()
            f = open(path, 'w')
            for i in arr:
                f.write(i)
            f.close()


    def windows_path(self, path: str = 'tasks/mat_demo_task.txt'):
        try:
            f = open(path, 'r')
        except FileNotFoundError:
            path_update = input('Путь неверный\nВведи путь вручную: ')
            f = open(path_update, 'r')
            arr = f.readlines()
            for i in range(3, len(arr), 4):
                arr[i] = arr[i].replace('/', '\\')
            f.close()
            f = open(path_update, 'w')
            for i in arr:
                f.write(i)
            f.close()

        else:
            arr = f.readlines()
            for i in range(3, len(arr), 4):
                arr[i] = arr[i].replace('/', '\\')
            f.close()
            f = open(path, 'w')
            for i in arr:
                f.write(i)
            f.close()


rep = Repaier()