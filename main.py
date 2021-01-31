import utils.callittea as tea
import argparse

def main():
    updater = tea.callittea(args.config, args.jenkins, args.telegram)
    updater.initial()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='callittea - Приложение для отлова обновлений в репозиториях Kallithea')
    parser.add_argument('--config', dest='config', default='./conf.d/config.json', metavar='config.json', help='Файл конфигурации')
    parser.add_argument('--without-jenkins', dest='jenkins', default=0, metavar='', help='Добавлять записи в БД без передачи задач в Jenkins')
    parser.add_argument('--without-telegram', dest='telegram', default=0, metavar='', help='Добавлять записи в БД без отправки оповещений в Telegram')
    args = parser.parse_args()
    if args.config:
        main()
    else:
        parser.print_help()
