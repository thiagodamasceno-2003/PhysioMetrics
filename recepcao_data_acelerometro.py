import time
import socket
from collections import deque

# Configurações
IP = "192.168.4.1"  # IP do Arduino
PORT = 23
BUFFER_SIZE = 1024
MAX_READINGS = 100000  # Número máximo de leituras a armazenar

# Buffer para armazenar dados recebidos
buffer = ""
leituras = deque(maxlen=MAX_READINGS)  # Lista circular eficiente

t_inicial = time.time()

def process_data(data):
    global buffer
    buffer += data.decode('utf-8', errors='replace')  # Adiciona ao buffer com tratamento de erros
#     buffer += f'{time.time()-t_inicial}'
    
    # Processa linhas completas (assumindo que o Arduino envia com \n)
    lines = buffer.split('\n')
    if len(lines) > 1:
        # Todas as linhas exceto a última estão completas
        for line in lines[:-1]:
            if line.strip():  # Ignora linhas vazias
                t = time.time()-t_inicial
                line = line[:-2]
                line += f',{t:.2f}'
                line += '\n'
                leituras.append(line.strip())  # Armazena a leitura
        
        # Mantém a última linha (incompleta) no buffer
        buffer = lines[-1]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((IP, PORT))
    print(f"Conectado ao Arduino {IP}:{PORT}")
    
    try:
        while True:
            data = s.recv(BUFFER_SIZE)
            if not data:
                break
            process_data(data)
            
    except KeyboardInterrupt:
        print("\nConexão encerrada pelo usuário")
    finally:
        # Salva todas as leituras em arquivo ao final
        with open('leituras_arduino.txt', 'w') as f:
            f.write('\n'.join(leituras))
        print(f"Leituras salvas em 'leituras_arduino.txt'")