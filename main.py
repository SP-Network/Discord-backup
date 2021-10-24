import requests, random, time, sys, os

token = '' # Tu token de Discord

def save_friends():
    saved_friends = 0

    friends = requests.get('https://discord.com/api/v6/users/@me/relationships', headers = headers)
    for friend in friends.json():
        if friend['type'] == 1:
            username = 'Username: %s#%s | User ID: %s\n' % (friend['user']['username'], friend['user']['discriminator'], friend['id'])
            sys.stdout.write(username)
            with open('Discord Friends.txt', 'a', encoding = 'UTF-8') as f:
                f.write(username)
            saved_friends += 1

    with open('Discord Friends.txt', 'r', encoding = 'UTF-8') as f:
        fixed = f.read()[:-1]
    with open('Discord Friends.txt', 'w', encoding = 'UTF-8') as f:
        f.write(fixed)

    sys.stdout.write('\n> Se guardaron exitosamente %s amigos de discord.\n\n' % (saved_friends))

def save_servers():
    saved_servers = 0
    attempts = 0
    server_info_all = ''

    servers = requests.get('https://discordapp.com/api/v6/users/@me/guilds', headers = headers)
    for server in servers.json():
        server_info_all += '%s|||%s\n' % (server['id'], server['name'])

    payload = {
        'max_age': '0',
        'max_uses': '0',
        'temporary': False
    }

    for server_info in server_info_all.splitlines():
        server_id = server_info.split('|||')[0]
        server_name = server_info.split('|||')[1]

        channels = requests.get('https://discord.com/api/v6/guilds/%s/channels' % (server_id), headers = headers)
        for channel in channels.json():
            if channel['type'] == 0:
                channel_id = channel['id']
                invite = requests.post('https://discord.com/api/v6/channels/%s/invites' % (channel_id), json = payload, headers = headers)
                
                if invite.status_code == 403:
                    attempts += 1
                    sys.stdout.write('Discord Server: %s | ID DEL CANAL: %s | Reintentando . . .\n' % (server_name, channel_id))
                    if attempts == 5:
                        sys.stdout.write('%s has a Vanity URL.\n' % (server_name))
                        with open('Discord Servers.txt', 'a', encoding = 'UTF-8') as f:
                            f.write('Discord Server: %s | Vanity URL\n' % (server_name))
                        saved_servers += 1
                        attempts = 0
                        break
                    else:
                        pass
                    time.sleep(4)
                
                elif invite.status_code == 429:
                    sys.stdout.write('Rate limited.\n')
                    time.sleep(9)
                
                else:
                    invite_url = 'https://discord.gg/%s' % (str(invite.json()['code']))
                    sys.stdout.write('Discord Server: %s | Invitacion: %s\n' % (server_name, invite_url))
                    with open('Discord Servers.txt', 'a', encoding = 'UTF-8') as f:
                        f.write('Discord Server: %s | ID DEL CANAL: %s | Invitacion: %s\n' % (server_name, channel_id, invite_url))
                    saved_servers += 1
                    time.sleep(4)
                    break

    sys.stdout.write('\n> Se guardaron exitosamente %s servidores de discord.\n\n' % (saved_servers))

def add_friends():
    added_friends = 0

    if os.path.exists('Discord Friends.txt'):
        with open('Discord Friends.txt', 'r', encoding = 'UTF-8') as f:
            for line in f.readlines():
                while True:
                    try:
                        line = line.replace('\n', '')
                        user_id = line.split('User ID: ')[1]
                        user_name = line.split(' |')[0]
                    except IndexError:
                        sys.stdout.write('Error de sintax en la linea: %s\n' % (line))
                        break
                    
                    add = requests.put('https://discord.com/api/v6/users/@me/relationships/%s' % (user_id), json = {}, headers = headers)
                    if add.status_code == 429:
                        sys.stdout.write('Rate limited.\n')
                        time.sleep(10)
                    elif add.status_code == 204:
                        sys.stdout.write('Solicitud de amistad enviada a: %s\n' % (user_name))
                        added_friends += 1
                        break
                    elif add.status_code == 400:
                        sys.stdout.write('El usuario ha inhabilitado las solicitudes de amistad: %s\n' % (user_name))
                        break
                    elif add.status_code == 403:
                        sys.stdout.write('Verifica tu cuenta de Discord.\n')
                        break
                    else:
                        sys.stdout.write('Error: %s\n' % (add.text))
                        break

                delay = random.randint(30, 35)
                time.sleep(delay)
        
        sys.stdout.write('\n> Añadi a %s Amigos de Discord.\n\n' % (added_friends))
    
    else:
        sys.stdout.write('> No has guardado ningún amigo..\n\n')

def join_servers():
    joined_servers = 0

    if os.path.exists('Discord Servers.txt'):
        with open('Discord Servers.txt', 'r', encoding = 'UTF-8') as f:
            for line in f.readlines():
                while True:
                    try:
                        line = line.replace('\n', '')
                        if 'Vanity URL' in line:
                            sys.stdout.write('El servidor tiene una URL personalizada.\n')
                            break
                        else:
                            invite_code = line.split('https://discord.gg/')[1]
                            server_name = line.split('Discord Server: ')[1].split(' | ID DEL CANAL')[0]
                    except IndexError:
                        sys.stdout.write('Error de sintax en la linea: %s\n' % (line))
                        break
                    
                    join = requests.post('https://discord.com/api/v6/invites/%s' % (invite_code), headers = headers)
                    if join.status_code == 429:
                        sys.stdout.write('Rate limited.\n')
                        time.sleep(10)
                    elif join.status_code == 200:
                        sys.stdout.write('Entre con exito a: %s\n' % (server_name))
                        joined_servers += 1
                        break
                    elif join.status_code == 403:
                        sys.stdout.write('Verifica tu cuenta de Discord.\n')
                        break
                    else:
                        sys.stdout.write('Error: %s\n' % (join.text))
                        break

                delay = random.randint(40, 45)
                time.sleep(delay)

        sys.stdout.write('\n> Entre con exito a %s Discord servers.\n\n' % (joined_servers))

    else:
        sys.stdout.write('> You have not saved any servers.\n\n')

while True:
    os.system('title [Discord Account Backup Bot] - Menu Principal')
    headers = { 'authorization': token }
    connect = requests.get('https://canary.discordapp.com/api/v6/users/@me', headers = headers)

    if connect.status_code == 200:
        option = str(input('[1] Guardar Amigos\n[2] Guardar Servidores\n\n[3] Añadir Amigos\n[4] Entrar a Servidores\n\n> Seleciona una opcion: '))
        sys.stdout.write('\n')
        if option == '1' or option == 'Guardar Amigos':
            os.system('title [Discord Account Backup Bot] - Guardar Amigos')
            save_friends()
        elif option == '2' or option == 'Guardar Servidores':
            os.system('title [Discord Account Backup Bot] - Guardar Servidores')
            save_servers()
        elif option == '3' or option == 'Añadir Amigos':
            os.system('title [Discord Account Backup Bot] - Añadir Amigos')
            add_friends()
        elif option == '4' or option == 'Entrar a Servidores':
            os.system('title [Discord Account Backup Bot] - Entrar a Servidores')
            join_servers()
        else:
            sys.stdout.write('> Opcion Invalida.\n\n')

    else:
        sys.stdout.write('> Token Invalido\n')
        token = str(input('Discord token: '))
        sys.stdout.write('\n')
