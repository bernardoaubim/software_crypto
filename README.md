# Criptografia 
- o **arquivo** é cifrado com **AES-CTR** (chave de 128 ou 256 bits);
- a **chave AES** e o **IV** são cifrados com **RSA-OAEP (SHA-256)**, usando a chave pública do destinatário.

O programa tem tudo em um único arquivo: `criptografia.py`.

---

## 1. Instalação (Windows)

### 1.1 Instalar o Python

1. Baixe o instalador em <https://www.python.org/downloads/>.
2. Na primeira tela do instalador, **marque a opção "Add python.exe to PATH"**.
3. Clique em **Install Now** e aguarde terminar.

Para conferir, abra o **Prompt de Comando** (tecla Windows, digite `cmd`, Enter) e rode:

```
python --version
```

Deve aparecer algo como `Python 3.12.x`. Se der erro, tente `py --version`. Se esse funcionar, use `py` no lugar de `python` nos comandos abaixo.

> O `tkinter` (usado para abrir a janela de escolha de arquivos) já vem com o Python do Windows. Não precisa instalar.

### 1.2 Instalar a biblioteca de criptografia

No Prompt de Comando:

```
pip install cryptography
```

---

## 2. Como executar

1. Coloque o `criptografia_simples.py` em uma pasta, por exemplo `C:\Tarefa3`.
2. Abra o Prompt de Comando **dentro dessa pasta**. 
3. Rode:

```
python criptografia_simples.py
```

O menu aparece:

```
1. Gerar par de chaves (RSA)
2. Cifrar arquivo com AES-CTR
3. Proteger chave/IV com chave pública
4. Recuperar chave/IV com chave privada
5. Decifrar arquivo com AES-CTR
0. Sair
```

Nas opções 2 a 5, o programa abre a janela do Windows para você **escolher o arquivo** com o mouse. Se você cancelar a janela, volta ao menu.

---

## 3. Passo a passo de uso

Exemplo com duas pessoas: **Alice** (envia o arquivo) e **Bob** (recebe).

### Bob (destinatário), uma única vez

1. Opção **1**, digite o nome `Bob`.
   - Gera `Bob.pu` (chave pública) e `Bob.pr` (chave privada).
2. Envia o **`Bob.pu`** para a Alice.
   - **Nunca envie o `Bob.pr`.** Ele é o segredo do Bob.

### Alice (quem cifra)

1. Opção **2**: escolha o arquivo (ex.: `x.txt`) e o tamanho da chave (`128` ou `256`).
   - Gera `x_K.txt` (chave AES), `x_IV.txt` (IV) e `x_Y.bin` (arquivo cifrado).
2. Opção **3**: escolha `x_K.txt` e depois o `Bob.pu`.
   - Gera `x_K.txt.rsa`.
3. Opção **3** de novo: escolha `x_IV.txt` e o `Bob.pu`.
   - Gera `x_IV.txt.rsa`.
4. Apague `x_K.txt` e `x_IV.txt` (estão em claro).
5. Envia ao Bo os três arquivos: **`x_Y.bin`**, **`x_K.txt.rsa`** e **`x_IV.txt.rsa`**.

### Bob (quem decifra)

1. Opção **4**: escolha `x_K.txt.rsa` e depois o `Bob.pr`.
   - Gera `x_K.txt`.
2. Opção **4** de novo: escolha `x_IV.txt.rsa` e o `Bob.pr`.
   - Gera `x_IV.txt`.
3. Opção **5**: escolha `x_Y.bin`, depois `x_K.txt`, depois `x_IV.txt`.
   - Gera `x_decifrado.txt`, o texto original.

---

## 4. Arquivos gerados

| Arquivo | O que é |
|---|---|---|
| `Nome.pu` | Chave pública RSA | 
| `Nome.pr` | Chave privada RSA | 
| `x_K.txt` | Chave AES em hexadecimal | 
| `x_IV.txt` | IV em hexadecimal | 
| `x_Y.bin` | Arquivo cifrado com AES-CTR | 
| `x_K.txt.rsa` / `x_IV.txt.rsa` | Chave e IV cifrados com RSA | 
| `x_decifrado.txt` | Texto original recuperado | 

---

## 5. Problemas comuns

| Mensagem | Causa e solução |
|---|---|
| `'python' não é reconhecido...` | Python não está no PATH. Reinstale marcando "Add python.exe to PATH", ou use `py`. |
| `ModuleNotFoundError: No module named 'cryptography'` | Rode `pip install cryptography`. |
| `Erro: Nenhum arquivo selecionado.` | Você fechou a janela de escolha sem selecionar. Tente de novo. |
| `Erro: Encryption/decryption failed` ao recuperar | A chave privada não é a par da chave pública usada, ou o arquivo `.rsa` está errado. |
| Texto decifrado ilegível | Chave, IV ou arquivo cifrado errados. O AES-CTR não avisa quando isso acontece. |
| A janela de escolha não aparece | Ela pode ter ficado atrás de outras janelas. Olhe a barra de tarefas. |

---


