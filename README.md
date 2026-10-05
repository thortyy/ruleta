# Ruleta

Jednoduchá evropská ruleta s lokálním Python serverem a virtuálními žetony.

## Spuštění

Vyžaduje Python 3.10 nebo novější. Další balíčky nejsou potřeba.

```powershell
python casino.py
```

Server otevře kasino na adrese `http://127.0.0.1:8765`. Ukončíš ho pomocí `Ctrl+C`.

## Testy

```powershell
python casino.py --test
```

Zůstatek a historii ukládá lokální soubor `casino_save.json`. Hraje se pouze o virtuální žetony; kasino nepřijímá vklady ani nevyplácí peníze.