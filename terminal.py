import pygame
import random
import time
import json
import os
import sys

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Terminal v1.4")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
WHITE = (255, 255, 255)
FONT = pygame.font.SysFont("consolas", 20)
BIGFONT = pygame.font.SysFont("consolas", 40)

SAVE_DIR = "saves"
SAVE_FILE = os.path.join(SAVE_DIR, "fast_save.json")
os.makedirs(SAVE_DIR, exist_ok=True)

command_desc = {
    'help': 'help [cmd] - показать все команды или описание конкретной.',
    'echo': 'echo <text> - повторить введенный текст.',
    'scan': 'scan - сканировать текущую зону на наличие директорий.',
    'ls': 'ls - показать список элементов в текущей директории.',
    'cd': 'cd <dir> - перейти в поддиректорию или cd .. для возврата.',
    'cat': 'cat <file> - вывести содержимое файла.',
    'glitch': 'glitch - вызвать визуальный и звуковой глитч. (ТЕСТ КОМАНДА)',
    'hint': 'hint - получить подсказку один раз.',
    'connect': 'connect <IP> - подключиться к удаленному узлу.',
    'passcode': 'passcode <code> - ввести код доступа.',
    'decrypt': 'decrypt <file> - расшифровать указанный файл.',
    'reboot': 'reboot - перезагрузить терминал (может изменить концовку).',
    'save': 'save - сохранить прогресс.',
    'load': 'load - загрузить прогресс.',
    'reply': 'reply watcher <msg> - ответить на поступающие сообщения (Если есть).',
    'secret': 'secret - ??? (секретная команда)',
    'bootcore': 'bootcore - запустить конечную последовательность.',
    'escape': 'escape - ??? (секретная команда)',
    'melt': 'melt - ??? (секретная команда)'
}

def draw_text(text, x, y, color=GREEN, font=FONT):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))


def draw_center(text, y, color=GREEN, font=FONT):
    surf = font.render(text, True, color)
    x = (WIDTH - surf.get_width()) // 2
    screen.blit(surf, (x, y))

def draw_multiline(lines, x, y, color=GREEN, font=FONT):
    for i, line in enumerate(lines):
        draw_text(line, x, y + i * (font.get_height() + 2), color, font)

def play_noise(duration_ms=200):
    sr = 44100
    n = int(sr * duration_ms / 1000)
    buf = bytearray()
    for _ in range(n): buf.append(128 + int(127 * random.uniform(-1,1)))
    sound = pygame.mixer.Sound(buffer=bytes(buf))
    sound.play()

progress = {
    'got_hint': False,
    'met_entity': False,
    'replied_once': False,
    'warned': False,
    'unlocked_log47': False,
    'decrypted_secret': False,
    'found_secret_sys': False,
    'end_triggered': False,
    'bootcore_count': 0
}

virtual_fs = {
    'root': {
        'log1.txt': '[LOG1] Boot OK. Welcome, guest.',
        'zoneA': { 'note.sys': "'Они задерживаются в ядре.' - xGhost", 'access.dat': '314159265' },
        'zoneB': { 'log47.txt': '[ENCRYPTED]', 'hint.txt': 'Ядро нестабильно. Найдите secret.sys в зоне C.' },
        'zoneC': { 'secret.sys': '' }
    }
}
current_path = ['root']
command_history = []
console_output = []
input_text = ''

def save_game():
    data = {'progress':progress, 'path':current_path, 'history':console_output[-50:]}
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    console_output.append(f"[SYSTEM] Сохранено в {SAVE_FILE}")


def load_game():
    if not os.path.exists(SAVE_FILE): console_output.append('[SYSTEM] Сохранение не найдено.'); return
    with open(SAVE_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
    progress.update(data.get('progress', {}))
    global current_path; current_path = data.get('path', ['root'])
    console_output.extend(['[SYSTEM] Загрузка завершена.'] + data.get('history', []))

def dark_end():
    console_output.append('[DARK END] Ядро поглощает тебя...')
    for _ in range(20):
        draw_multiline(['CORE OVERRIDE...']*10, 100, 100)
        pygame.display.flip(); play_noise(50); time.sleep(0.05)
    sys.exit(0)


def loop_end():
    console_output.clear(); console_output.append('[LOOP END] Ты в ловушке, навсегда.')
    time.sleep(1)
    main()


def secret_end():
    console_output.append('[SECRET END] True Good End: Архив раскрывает правду..')
    time.sleep(2)
    sys.exit(0)


def super_secret():
    for i in range(30):
        screen.fill(BLACK)
        for _ in range(100):
            x = random.randint(0, WIDTH); y = random.randint(0, HEIGHT)
            draw_text(random.choice(['#','@','%','*','?']), x, y)
        pygame.display.flip(); time.sleep(0.05)
    screen.fill((255,0,0)); pygame.display.flip(); play_noise(1000); time.sleep(1); sys.exit(0)

def get_node():
    node = virtual_fs
    for p in current_path: node = node[p]
    return node


def execute(cmd):
    global current_path
    command_history.append(cmd)
    parts = cmd.split(); c = parts[0].lower() if parts else ''; args = parts[1:]

    if c == 'help':
        if args:
            name = args[0].lower()
            desc = command_desc.get(name, f"Нет информации о '{name}'.")
            console_output.append(desc)
        else:
            console_output.append('Available commands:')
            for name in sorted(command_desc.keys()): console_output.append(' ' + name)

    elif c == 'echo': console_output.append(' '.join(args))

    elif c == 'scan':
        console_output.append('[SCAN] обнаружение зон...'); time.sleep(0.3)
        dirs = [k for k,v in get_node().items() if isinstance(v, dict)]
        console_output.append('Zones: ' + ','.join(dirs))
        if not progress['met_entity']:
            console_output.extend(['[INCOMING TRANSMISSION...]','[???]: Гость... Ядро просыпается.'])
            progress['met_entity'] = True

    elif c == 'ls': console_output.append(' '.join(get_node().keys()))

    elif c == 'cd':
        if not args: console_output.append('Укажите папку.')
        elif args[0] == '..' and len(current_path) > 1: current_path.pop()
        elif args[0] in get_node() and isinstance(get_node()[args[0]], dict): current_path.append(args[0])
        else: console_output.append('Нет такой директории.')

    elif c == 'cat':
        if not args: console_output.append('Укажите файл.')
        else:
            nm = args[0]; node = get_node()
            if nm == 'secret.sys' and 'secret.sys' in node:
                console_output.append(node[nm] or '(пусто)'); progress['found_secret_sys'] = True
                virtual_fs['root']['archive.sys'] = '[ARCHIVE] Истина симуляции скрыта.'
            elif nm == 'archive.sys':
                secret_end()
                return
            else:
                if nm in node and isinstance(node[nm], str):
                    if nm == 'log47.txt' and not progress['unlocked_log47']:
                        console_output.append('[ДОСТУП ЗАПРЕЩЕН]')
                    else:
                        console_output.append(node[nm] or '(пусто)')
                else:
                    console_output.append('Файл не найден.')

    elif c == 'hint':
        if not progress['got_hint']:
            console_output.append('Используй команду connect 192.168.0.47 и команду passcode 314159265.')
            progress['got_hint'] = True
        else: console_output.append('Подсказок больше нет.')

    elif c == 'connect':
        if args and args[0] == '192.168.0.47':
            console_output.append('Подключение...'); time.sleep(0.4)
            console_output.append('[CONNECTED]'); progress['unlocked_log47'] = True
        else: console_output.append('Не удалось подключиться.')

    elif c == 'passcode':
        if args and args[0] == '314159265': console_output.append('Код принят. decrypt доступен.'); progress['unlocked_log47'] = True
        else: console_output.append('Неверный код.')

    elif c == 'decrypt':
        if args and args[0]=='log47.txt' and progress['unlocked_log47']:
            console_output.append('Расшифровка...'); time.sleep(0.5)
            console_output.append("[DECRYPTED] 'Ядро пробуждается по вашей команде.'")
            progress['decrypted_secret']=True
            virtual_fs['root']['zoneC']['secret.sys'] = "[SECRET] 'Бегите когда будете готовы.'"
        else: console_output.append('Нечего расшифровывать.')

    elif c == 'reply':
        if not progress['met_entity']: console_output.append('[ERROR] Никто не слушает. Ответа нет.')
        elif len(args)<2 or args[0].lower()!='watcher': console_output.append('Usage: reply watcher <message>')
        else:
            msg=' '.join(args[1:]).lower()
            if not progress['replied_once']:
                console_output.extend(['[???]: Приветствую.. Меня зовут Watcher..','[Watcher]: Найди один фрагмент в zoneA в access.dat..']); progress['replied_once']=True
            elif 'decrypt' in msg and not progress['warned']:
                console_output.append('[Watcher]: Ты близкок. Но уже слишком поздно.'); progress['warned']=True
            else: console_output.append(f"[Watcher]: Но все же я не понимаю почему- '{msg}'.")
            if progress['replied_once'] and progress['warned']:
                console_output.append('[CONNECTION LOST]'); progress['met_entity']=False

    elif c == 'bootcore':
        if progress['decrypted_secret'] and progress['found_secret_sys']:
            console_output.append('ЗАГРУЗКА ЯДРА...'); progress['end_triggered']=True; progress['bootcore_count']=0
        else: console_output.append('Условия не выполнены.')

    elif c == 'escape':
        if progress['end_triggered']: console_output.append('Вы сбежали из симуляции. GOOD END.'); sys.exit(0)
        else: console_output.append('Невозможно сбежать сейчас.')

    elif c == 'glitch':
        if progress['end_triggered']:
            progress['bootcore_count']+=1
            if progress['bootcore_count']>=3: loop_end(); return
        for _ in range(3): console_output.append(random.choice(['[GLTCH]','##@!$','((()))'])); play_noise()

    elif c == 'reboot':
        if progress['end_triggered']: dark_end(); return
        console_output.append('Перезагрузка...'); time.sleep(1); console_output.clear(); console_output.append('[SYSTEM] Boot complete.'); current_path=['root']

    elif c == 'melt': super_secret(); return

    elif c == 'save': save_game()
    elif c == 'load': load_game()

    else: console_output.append(f"Неизвестная команда: {c}")

def disclaimer():
    screen.fill(BLACK)
    for i,l in enumerate(['ВНИМАНИЕ!','Глитчи и шумы впереди.','Нажмите ENTER для продолжения.']): draw_center(l, HEIGHT//3 + i*30, GREEN)
    pygame.display.flip()


def main_menu():
    screen.fill(BLACK)
    opts=['Новая игра','Загрузить','Выход']
    draw_center('Terminal',100,WHITE,BIGFONT)
    for i,o in enumerate(opts): draw_center(o,200+i*40, GREEN if i==main_menu.sel else DARK_GREEN)
    pygame.display.flip()

def bios_intro():
    screen.fill(BLACK)
    for i,s in enumerate(['ПОСЛЕДОВАТЕЛЬНОСТЬ ЗАГРУЗКИ...','ЗАГРУЗКА МОДУЛЕЙ...', 'ИНИТАЦИЯ ЯДРА...', 'СИСТЕМА ОНЛАЙН']): draw_center(s,150+i*50,WHITE,BIGFONT); pygame.display.flip(); time.sleep(0.5)
    time.sleep(0.2)

def render_console():
    screen.fill(BLACK)
    draw_multiline(console_output[-25:],20,20)
    draw_text('> '+input_text,20,HEIGHT-40)
    pygame.display.flip()

def main():
    state='disclaimer'; main_menu.sel=0
    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); return
            if e.type==pygame.KEYDOWN:
                if state=='disclaimer' and e.key==pygame.K_RETURN: state='menu'
                elif state=='menu':
                    if e.key==pygame.K_UP: main_menu.sel=(main_menu.sel-1)%3
                    elif e.key==pygame.K_DOWN: main_menu.sel=(main_menu.sel+1)%3
                    elif e.key==pygame.K_RETURN:
                        if main_menu.sel==0: state='bios'; break
                        if main_menu.sel==1: load_game(); state='console'; break
                        if main_menu.sel==2: pygame.quit(); return
                elif state=='bios' and e.key==pygame.K_RETURN: bios_intro(); console_output.clear(); state='console'; break
                elif state=='console':
                    global input_text
                    if e.key==pygame.K_RETURN: execute(input_text); input_text=''
                    elif e.key==pygame.K_BACKSPACE: input_text=input_text[:-1]
                    else: input_text+=e.unicode
        if state=='disclaimer': disclaimer()
        elif state=='menu': main_menu()
        elif state=='console': render_console()

if __name__=='__main__': main()
