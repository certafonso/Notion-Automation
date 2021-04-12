from settings import *
from notion.client import NotionClient
from notion import block, collection
from datetime import datetime

def main():
    today = datetime.today()
    today_notion = collection.NotionDate(today)
    today_str = today.strftime(DATE_FORMAT_STR)

    print(f"Notion automation script starting for {today_str}")

    # get client and collection view
    client = NotionClient(token_v2=TOKEN)
    cv = client.get_collection_view(LIST_URL)

    print(f"Collection view with id {cv.id} retrieved")

    # get last day's page
    sort_params = [{
        "direction": "descending",
        "property": "date",
    }]

    last_day = cv.build_query(sort=sort_params).execute()[0]

    print(f"Retrieved last day: {last_day.title}")

    if today_str == last_day.title:
        print("Last day is today, stopping...")
        return

    # create today's page
    today_page = cv.collection.add_row()
    today_page.title = today_str
    today_page.date = today_notion

    print("Created today's page")
    
    # copy contents
    for child in last_day.children: CopyBlock(child, today_page)

def CopyBlock(original_block, dest_block):
    """ Copies a block """

    if type(original_block) == block.TodoBlock and original_block.checked:
        return

    new_block = dest_block.children.add_new(type(original_block))

    # type has title
    if type(original_block) in [block.ToggleBlock, block.TodoBlock]:
        new_block.title = original_block.title

    # type has children
    if type(original_block) in [block.ColumnBlock, block.ColumnListBlock, block.ToggleBlock]:
        for child in original_block.children:
            CopyBlock(child, new_block)

    print(f"Copied block with id: {original_block.id}")

if __name__ == "__main__":
    main()
