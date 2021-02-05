import utils.callittea as tea
import argparse
import schedule
import time

def main():
    updater = tea.callittea(args.config)
    updater.initial()


def init():
    schedule.every(int(args.sleep)).seconds.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='callittea - Приложение для отлова обновлений в репозиториях Kallithea')
    parser.add_argument('--config', dest='config', default='./conf.d/config.json', metavar='config.json', help='Файл конфигурации')
    parser.add_argument('--sleep', dest='sleep', type=int, default=300, metavar='60', help='Задержка между проверками (сек)')
    args = parser.parse_args()
    if args.config:
        init()
    else:
        parser.print_help()
