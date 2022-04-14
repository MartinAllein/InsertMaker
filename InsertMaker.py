from classes.ItemBox import ItemBox
from classes.CardBox import CardBox
from classes.CardSheet import CardSheet
from classes.Design import Design

if __name__ == "__main__":
    outfile = ""

    # -l141 -w 97 -h 17.5 -d 5 -s 1.5 -o mbox
    # itembox = ItemBox("-c ItemBox -C ITEMBOX -v")
    # itembox.create()

    # -l90 -w 60 -h 25.5  -b -f 20 -F 30 -u 5 -n 6 -o cardBox -c CardBox -C CARDBOX -v
    # cardbox = CardBox("-c CardBox -C CARDBOX")
    # cardbox.create()

    cardsheet = CardSheet()
    cardsheet.create()

