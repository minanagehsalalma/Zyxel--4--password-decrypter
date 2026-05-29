# Zyxel WAX650S $4$ Encrypted Password Decrypter

This repository contains a Python CLI for decrypting passwords stored with Zyxel's proprietary `$4$` scheme, commonly found in `mfg-default.conf` configuration files on Zyxel WAX650S devices and potentially other Zyxel products.

## Background

The `$4$` scheme is used by Zyxel to store sensitive information, such as administrative passwords, in a reversible encrypted format rather than a one-way hash. Analysis of Zyxel firmware has revealed that this scheme utilizes **AES-192-CBC** encryption with a static key and Initialization Vector (IV) embedded within the `zysh` binary.

This tool was developed from public firmware-analysis research, then packaged here as a reusable CLI instead of a one-off hard-coded sample.

## Technical Details

The encryption process involves:
1.  **Salt**: An 8-byte ASCII salt is extracted from the `$4$` string.
2.  **Plaintext Preparation**: The plaintext password is combined with the salt and then padded or repeated to fill an 80-byte buffer.
3.  **Encryption**: AES-192-CBC is applied to the prepared plaintext using a static key and IV.
4.  **Encoding**: The resulting ciphertext is Base64 encoded.

### Identified AES Parameters

| Parameter | Value |
| :-------- | :---- |
| **Algorithm** | AES-192-CBC |
| **Key (Hex)** | `001200054A1F23FB1F060A14CD0D018F5AC0001306F0121C` |
| **IV (Hex)** | `0006001C01F01FC0FFFFFFFFFFFFFFFF` |

## Usage

### Prerequisites

- Python 3.x
- `pycryptodome` library: `pip install pycryptodome`

### Input formats

The CLI accepts either:

- the full `$4$<salt>$<cipher>$` value
- an entire config line containing that `$4$...$...$` fragment
- the Base64 ciphertext alone, together with `--salt`

### Decrypt a full `$4$` string

```bash
python3 zyxel_decrypter.py '$4$WliGKvFQ$yMEH/WCnH1+NXuIUp0lzpUinIyEnrHFoRgesi6NdOFytmQg8lRfsVzUUjBGY+FiS4Up6KIgoP8OMEP0L3hRYSN2kpFTDIet31GoNwlM+S7U$'
```

### Decrypt from a config line

```bash
python3 zyxel_decrypter.py 'username admin encrypted-password $4$WliGKvFQ$yMEH/WCnH1+NXuIUp0lzpUinIyEnrHFoRgesi6NdOFytmQg8lRfsVzUUjBGY+FiS4Up6KIgoP8OMEP0L3hRYSN2kpFTDIet31GoNwlM+S7U$ user-type admin'
```

### Decrypt with separate salt and ciphertext

```bash
python3 zyxel_decrypter.py 'yMEH/WCnH1+NXuIUp0lzpUinIyEnrHFoRgesi6NdOFytmQg8lRfsVzUUjBGY+FiS4Up6KIgoP8OMEP0L3hRYSN2kpFTDIet31GoNwlM+S7U' --salt WliGKvFQ
```

### Show the raw decrypted buffer

```bash
python3 zyxel_decrypter.py '$4$WliGKvFQ$yMEH/WCnH1+NXuIUp0lzpUinIyEnrHFoRgesi6NdOFytmQg8lRfsVzUUjBGY+FiS4Up6KIgoP8OMEP0L3hRYSN2kpFTDIet31GoNwlM+S7U$' --raw
```

The CLI prints the extracted salt and recovered plaintext password. `--raw` adds the full decrypted buffer for validation work.

## Example

Given the config line:

`username admin encrypted-password $4$WliGKvFQ$yMEH/WCnH1+NXuIUp0lzpUinIyEnrHFoRgesi6NdOFytmQg8lRfsVzUUjBGY+FiS4Up6KIgoP8OMEP0L3hRYSN2kpFTDIet31GoNwlM+S7U$ user-type admin`

Running:

```bash
python3 zyxel_decrypter.py 'username admin encrypted-password $4$WliGKvFQ$yMEH/WCnH1+NXuIUp0lzpUinIyEnrHFoRgesi6NdOFytmQg8lRfsVzUUjBGY+FiS4Up6KIgoP8OMEP0L3hRYSN2kpFTDIet31GoNwlM+S7U$ user-type admin' --raw
```

will yield:

```
Salt: WliGKvFQ
Decrypted (raw): b'WliGKvFQ1234\x00123412341234123412341234123412341234123412341234123412341234123'
Decrypted Password: 1234
```

## Disclaimer

This tool is provided for educational and research purposes only. Use it responsibly and in accordance with applicable laws and regulations. The author is not responsible for any misuse or damage caused by this tool.

## References

[1] HN Security. *Zyxel firmware extraction and password analysis*. [https://hnsecurity.it/blog/zyxel-firmware-extraction-and-password-analysis/](https://hnsecurity.it/blog/zyxel-firmware-extraction-and-password-analysis/)
