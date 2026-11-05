import os
import tkinter as tk
from tkinter import filedialog
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# OAEP é o padding aplicado à mensagem antes do RSA. Ele adiciona aleatoriedades
OAEP = padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()), # função que gera as máscaras (MGF1 com SHA-256)
    algorithm=hashes.SHA256(), # hash usado na estrutura do bloco
    label=None,
)


# ------------------------------------------------------------ funções de apoio

def escolher_arquivo(titulo, tipos=(("Todos os arquivos", "*.*"),)):
    """Abre o gerenciador de arquivos (Windows, Linux ou macOS) e devolve o caminho."""
    janela = tk.Tk()
    janela.withdraw()                      # esconde a janelinha principal
    janela.attributes("-topmost", True)    # garante que o seletor apareça na frente
    caminho = filedialog.askopenfilename(title=titulo, filetypes=tipos)
    janela.destroy()
    if not caminho:
        raise ValueError("Nenhum arquivo selecionado.")
    return caminho


def ler(caminho):
    """Lê um arquivo como bytes."""
    with open(caminho, "rb") as f:
        return f.read()


def gravar(caminho, dados):
    """Grava bytes em um arquivo."""
    with open(caminho, "wb") as f:
        f.write(dados)


def ler_hex(caminho):
    """Lê um arquivo de texto com hexadecimal e devolve os bytes."""
    return bytes.fromhex(ler(caminho).decode().strip())


def gravar_hex(caminho, dados):
    """Grava bytes como texto hexadecimal."""
    gravar(caminho, dados.hex().encode())


def aes_ctr(dados, chave, iv):
    """Cifra ou decifra com AES-CTR (a operação é a mesma nos dois sentidos)."""
    operacao = Cipher(algorithms.AES(chave), modes.CTR(iv)).encryptor()
    return operacao.update(dados) + operacao.finalize()
           # Processa os dados      # encerra e devolve o que sobrou (não é para sobrar nada)

# ------------------------------------------------------------ opções do menu

def gerar_chaves():
    """1ª etapa: gera Nome.pu e Nome.pr (RSA 2048 bits)."""
    nome = input("Seu nome: ").strip()
    privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    pem_publica = privada.public_key().public_bytes(
        serialization.Encoding.PEM, # Define a codificação do arquivo
        serialization.PublicFormat.SubjectPublicKeyInfo, # Define a estrutura interna da chave pública
    )
    pem_privada = privada.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8, # Define a estrutura interna da chave privada
        serialization.NoEncryption(),
    )
    gravar(nome + ".pu", pem_publica)
    gravar(nome + ".pr", pem_privada)
    print(f"Geradas: {nome}.pu (pública) e {nome}.pr (privada, não envie!)")


def cifrar_arquivo():
    """2ª e 3ª etapas: cifra o arquivo com AES-CTR."""
    arquivo = escolher_arquivo("Escolha o arquivo a cifrar")
    bits = input("Tamanho da chave AES (128 ou 256): ").strip()
    if bits not in ("128", "256"):
        raise ValueError("Escolha 128 ou 256.")

    chave = os.urandom(int(bits) // 8)  # gera chave aleatória
    iv = os.urandom(16)                 # gera vetor de inicialização aleatório
    cifrado = aes_ctr(ler(arquivo), chave, iv)

    base = os.path.splitext(arquivo)[0] # splitext separa o nome da extensão. "C:\pasta\x.txt" vira ("C:\pasta\x", ".txt"), e [0] pega a primeira parte, sem a extensão.
    gravar_hex(base + "_K.txt", chave)
    gravar_hex(base + "_IV.txt", iv)
    gravar(base + "_Y.bin", cifrado)
    print(f"Criados: {base}_K.txt (chave), {base}_IV.txt (IV), {base}_Y.bin (cifrado)")


def proteger():
    """4ª etapa: cifra a chave ou o IV com a chave pública do destinatário."""
    arquivo = escolher_arquivo("Escolha o arquivo da chave ou do IV")
    caminho_pu = escolher_arquivo("Escolha a chave pública do destinatário", (("Chave pública", "*.pu"),))

    # Lê o arquivo .pu e reconstrói o objeto de chave pública RSA
    publica = serialization.load_pem_public_key(ler(caminho_pu))
    protegido = publica.encrypt(ler(arquivo), OAEP)
    gravar(arquivo + ".rsa", protegido)
    print(f"Criado: {arquivo}.rsa  (apague o original em claro antes de enviar)")


def recuperar():
    """Decifra a chave ou o IV com a chave privada."""
    arquivo = escolher_arquivo("Escolha o arquivo protegido", (("Arquivo RSA", "*.rsa"),))
    caminho_pr = escolher_arquivo("Escolha a sua chave privada", (("Chave privada", "*.pr"),))

    privada = serialization.load_pem_private_key(ler(caminho_pr), password=None)
    claro = privada.decrypt(ler(arquivo), OAEP)
    saida = arquivo[:-4]  # tira o ".rsa" do nome
    gravar(saida, claro)
    print(f"Recuperado: {saida}")


def decifrar_arquivo():
    """Decifra o arquivo com AES-CTR usando a chave e o IV recuperados."""
    cifrado = escolher_arquivo("Escolha o arquivo cifrado (_Y.bin)", (("Arquivo cifrado", "*.bin"),))
    chave = ler_hex(escolher_arquivo("Escolha o arquivo da chave AES"))
    iv = ler_hex(escolher_arquivo("Escolha o arquivo do IV"))

    saida = cifrado.replace("_Y.bin", "") + "_decifrado.txt"
    gravar(saida, aes_ctr(ler(cifrado), chave, iv))
    print(f"Decifrado: {saida}")


# ------------------------------------------------------------ programa principal

ACOES = {
    "1": gerar_chaves,
    "2": cifrar_arquivo,
    "3": proteger,
    "4": recuperar,
    "5": decifrar_arquivo,
}

while True:
    print("\n1. Gerar par de chaves (RSA)")
    print("2. Cifrar arquivo com AES-CTR")
    print("3. Proteger chave/IV com chave pública")
    print("4. Recuperar chave/IV com chave privada")
    print("5. Decifrar arquivo com AES-CTR")
    print("0. Sair")
    opcao = input("Opção: ").strip()

    if opcao == "0":
        break
    if opcao not in ACOES:
        print("Opção inválida.")
        continue
    try:
        ACOES[opcao]()
    except Exception as erro:  # mostra o problema sem derrubar o programa
        print(f"Erro: {erro}")
