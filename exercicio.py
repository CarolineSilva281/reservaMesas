import mysql.connector
from datetime import datetime
 
# Função de conexão
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="connector"
    )
 
# Validação de cpf simples
def validar_cpf(cpf):
    return len(cpf) == 11 and cpf.isdigit()
 
#se mesa existe
def mesa_existe(mesa_id):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM mesas WHERE id = %s", (mesa_id,))
    existe = cur.fetchone()[0] > 0
    con.close()
    return existe
 
# Listar mesas
def listar_mesas():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, nomeMesa, descricao, preco, disponibilidade FROM mesas")
    mesas = cur.fetchall()
    print("\n--- MESAS ---")
    for m in mesas:
        status = "Disponível" if m[4] else "Reservada"
        print(f"{m[0]} - {m[1]} | {m[2]} | R${m[3]:.2f} | {status}")
    con.close()
 
# Reserva mesa
def reservar_mesa():
    nome = input("Nome: ").strip()
    cpf = input("CPF (apenas números): ").strip()
    if not validar_cpf(cpf):
        print("CPF inválido!")
        return
 
    listar_mesas()
    mesa_id = input("Digite o ID da mesa desejada: ").strip()
 
    if not mesa_id.isdigit() or not mesa_existe(mesa_id):
        print("Mesa inválida!")
        return
 
    con = conectar()
    cur = con.cursor()
 
    # Verificar se mesa está disponível
    cur.execute("SELECT disponibilidade FROM mesas WHERE id = %s", (mesa_id,))
    if not cur.fetchone()[0]:
        print("Mesa já reservada!")
        con.close()
        return
 
    # Inserir ou recuperar cliente
    cur.execute("SELECT id FROM clientes WHERE cpf = %s", (cpf,))
    cliente = cur.fetchone()
    if cliente:
        cliente_id = cliente[0]
    else:
        cur.execute("INSERT INTO clientes (nome, cpf) VALUES (%s, %s)", (nome, cpf))
        cliente_id = cur.lastrowid
 
    # Atualizar mesa e registrar histórico
    cur.execute("UPDATE mesas SET disponibilidade = FALSE WHERE id = %s", (mesa_id,))
    cur.execute(
        "INSERT INTO historico_reservas (cliente_id, mesa_id, status) VALUES (%s, %s, 'ativa')",
        (cliente_id, mesa_id)
    )
    con.commit()
    print("Reserva feita com sucesso!")
    con.close()
 
# Cancelar reserva
def cancelar_reserva():
    cpf = input("Digite seu CPF: ").strip()
    if not validar_cpf(cpf):
        print("CPF inválido!")
        return
 
    con = conectar()
    cur = con.cursor()
 
    cur.execute("""
        SELECT h.id, m.id, m.nomeMesa
        FROM historico_reservas h
        JOIN clientes c ON h.cliente_id = c.id
        JOIN mesas m ON h.mesa_id = m.id
        WHERE c.cpf = %s AND h.status = 'ativa'
    """, (cpf,))
    reserva = cur.fetchone()
 
    if not reserva:
        print("Nenhuma reserva ativa encontrada.")
        con.close()
        return
 
    hist_id, mesa_id, mesa_nome = reserva
 
    cur.execute("UPDATE mesas SET disponibilidade = TRUE WHERE id = %s", (mesa_id,))
    cur.execute("UPDATE historico_reservas SET status = 'cancelada' WHERE id = %s", (hist_id,))
    con.commit()
    print(f"Reserva da {mesa_nome} cancelada com sucesso.")
    con.close()
 
# Listar reservas ativas
def listar_reservas():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT c.nome, m.nomeMesa, m.preco
        FROM historico_reservas h
        JOIN clientes c ON h.cliente_id = c.id
        JOIN mesas m ON h.mesa_id = m.id
        WHERE h.status = 'ativa'
    """)
    reservas = cur.fetchall()
    print("\n--- RESERVAS ATIVAS ---")
    for r in reservas:
        print(f"{r[0]} reservou {r[1]} (R${r[2]:.2f})")
    con.close()
 
# Listar histórico
def listar_historico():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT c.nome, m.nomeMesa, h.status, h.data_reserva
        FROM historico_reservas h
        JOIN clientes c ON h.cliente_id = c.id
        JOIN mesas m ON h.mesa_id = m.id
        ORDER BY h.data_reserva DESC
    """)
    historico = cur.fetchall()
    print("\n--- HISTÓRICO DE RESERVAS ---")
    for h in historico:
        print(f"{h[0]} - {h[1]} | {h[2]} | {h[3]}")
    con.close()
 
# Menu
def menu():
    while True:
        print("\n====== MENU ======")
        print("1 - Listar mesas")
        print("2 - Reservar mesa")
        print("3 - Cancelar reserva")
        print("4 - Listar reservas ativas")
        print("5 - Listar histórico")
        print("6 - Sair")
 
        opcao = input("Escolha: ").strip()
        if opcao == '1':
            listar_mesas()
        elif opcao == '2':
            reservar_mesa()
        elif opcao == '3':
            cancelar_reserva()
        elif opcao == '4':
            listar_reservas()
        elif opcao == '5':
            listar_historico()
        elif opcao == '6':
            break
        else:
            print("Opção inválida.")
 
menu()