from classes.ItemBox import ItemBox
from classes.CardBox import CardBox

if __name__ == "__main__":
    outfile = ""

    # -l141 -w 97 -h 17.5 -d 5 -s 1.5 -o mbox
    # itembox = ItemBox("-l141 -w 97 -h 17.5 -d 5 -s 1.5 -o mbox")
    # itembox.create()

    # -l140 -w 50 -h 18 -d10 -f 10 -F 20 -u 5 -n 4 -o cardBox
    cardbox = CardBox()
    cardbox.create()
