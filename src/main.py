from flet import *
import script
import os
import json

# Constants
WINDOW_HEIGHT = 745
WINDOW_WIDTH = 390
BG_COLOR = Colors.CYAN_50
BUTTON_WIDTH = 170
BUTTON_HEIGHT = 80
BUTTON_TEXT_SIZE = 36
BUTTON_FONT_FAMILY = "Arial"
BUTTON_BORDER_RADIUS = 3

# Load device types
path = os.path.dirname(os.path.abspath(__file__))
DTpath = os.path.join(path, "static", "devicetype.json")
with open(DTpath, "r", encoding="utf-8") as f:
    devicetype = json.load(f)


class AppState:
    def __init__(self):
        self.cust = "اشرف"  # Default customer
        self.index = 0  # Default index for tabs


def main(page: Page):
    page.title = "management"
    page.window.height = WINDOW_HEIGHT
    page.window.width = WINDOW_WIDTH
    page.bgcolor = BG_COLOR
    page.theme_mode = ThemeMode.LIGHT
    page.scroll = True
    state = AppState()

    def update_tabs(e):
        state.index = tabs.selected_index
        update_table(state.index)

    def update_table(selected_index=None):
        if selected_index is None:
            selected_index = state.index

        # Dynamically rebuild the tabs
        tabs.tabs = [
            Tab(
                content=table(i),
                text=str(i),
                height=50,
            )
            for i in script.get_tables(state.cust, device_dropdown.value)
        ]

        # Ensure the selected index is valid
        tabs.selected_index = (
            min(selected_index, len(tabs.tabs) - 1) if len(tabs.tabs) > 0 else 0
        )

        # Update the height of the tabs
        update_height(tabs.selected_index)
        page.update()

    def update_height(num):
        tabs.height = (
            80 * len(script.get_data(state.cust, device_dropdown.value, num)) + 60
        )
        tabs.height = 400 if tabs.height < 400 else tabs.height

    def update_cust(e):
        ashraf_button.bgcolor = (
            Colors.GREEN_ACCENT_700 if state.cust == "اشرف" else BG_COLOR
        )
        mahmoud_button.bgcolor = (
            Colors.GREEN_ACCENT_700 if state.cust == "محمود" else BG_COLOR
        )
        page.update()

    def close_sheet(e):
        new_total = new_total_input.value

        if not new_total.isdigit():
            show_error("يجب إدخال رقم صحيح!")
            return

        script.create_Table(state.cust, device_dropdown.value, int(new_total))

        update_stats(e)

        alert.open = False
        page.update()

    def show_new_total_dialog(e):
        new_total_input.value = ""
        alert.content = Column(
            controls=[new_total_input],
            tight=True,
            width=400,
        )
        page.overlay.append(alert)
        alert.open = True
        page.update()

    def show_new_total_dialog2(e):
        new_device_input.value = ""
        alert2.content = Column(
            [new_device_input],
            tight=True,
            width=400,
        )
        page.overlay.append(alert2)
        alert2.open = True
        page.update()

    def reload_devicetype(mess):
        with open(DTpath, "r", encoding="utf-8") as f:
            global devicetype
            devicetype = json.load(f)
        device_dropdown.options = [
            dropdown.Option(
                d,
                style=ButtonStyle(
                    text_style=TextStyle(size=20),
                    shape=RoundedRectangleBorder(1),
                    alignment=Alignment(5, 0),
                ),
            )
            for d in devicetype
        ]
        device_dropdown.value = new_device_input.value
        lambda e: update_stats(e)
        page.update()

    def update_stats(e):
        try:
            stats_row1.controls = [
                create_stat_card(
                    "العدد الكلي", script.show(state.cust, device_dropdown.value)[0]
                ),
                create_stat_card(
                    "اجمالي المبيعات", script.show(state.cust, device_dropdown.value)[1]
                ),
            ]

            stats_row2.controls = [
                create_stat_card(
                    "العدد الحالي", script.show(state.cust, device_dropdown.value)[2]
                ),
                create_stat_card(
                    "اجمالي السعر",
                    f"$ {script.show(state.cust, device_dropdown.value)[3]}",
                ),
            ]
            # Pass 0 explicitly to `update_table` to avoid passing `ControlEvent`
            update_table()
            # page.update()
        except Exception as e:
            print(f"Error updating stats: {e}")
            show_error("حدث خطأ في تحميل البيانات!")

    def create_stat_card(title, value):
        return Container(
            content=Column(
                controls=[
                    Text(
                        title,
                        size=20,
                        text_align=TextAlign.CENTER,
                        weight=FontWeight.BOLD,
                        color=Colors.BLACK,
                    ),
                    Text(
                        str(value),
                        size=30,
                        text_align=TextAlign.CENTER,
                        weight=FontWeight.BOLD,
                        color=Colors.GREEN,
                    ),
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER,
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=Colors.CYAN_ACCENT_100,
            border=border.all(1, Colors.BLACK),
            border_radius=10,
            padding=10,
            width=page.window.width / 2 - 30,
        )

    def show_error(message):
        alert = AlertDialog(
            title=Text("خطأ"),
            content=Text(message),
            actions=[TextButton("OK", on_click=lambda e: alert.close())],
        )
        page.dialog = alert
        alert.open = True
        page.update()

    new_total_input = TextField(
        label="العدد الكلي الجديد",
        keyboard_type=KeyboardType.NUMBER,
        text_align=TextAlign.RIGHT,
    )
    new_device_input = TextField(label="اسم الجهاز الجديد", text_align=TextAlign.LEFT)

    def close(al):
        al.open = False
        page.update()

    device_dropdown = Dropdown(
        options=[
            dropdown.Option(
                d,
                style=ButtonStyle(
                    text_style=TextStyle(
                        size=20,
                    ),
                    shape=RoundedRectangleBorder(1),
                    alignment=Alignment(5, 0),
                ),
            )
            for d in devicetype
        ],
        value="GT06N",
        width=page.window.width,
        menu_height=WINDOW_HEIGHT / 2,
        menu_width=WINDOW_WIDTH / 3,
        border_color=Colors.ORANGE,
        text_style=TextStyle(
            letter_spacing=2,
            size=24,
            weight=FontWeight.BOLD,
            font_family="Arial",
        ),
        on_change=update_stats,
    )

    alert = AlertDialog(
        title=Text(
            "إنشاء شيت جديد",
            text_align=TextAlign.RIGHT,
        ),
        adaptive=True,
        content_padding=20,
        actions_alignment="center",
        modal=True,
        shape=RoundedRectangleBorder(radius=10),
        actions=[
            Column(
                spacing=10,
                controls=[
                    TextButton(
                        "موافق",
                        on_click=close_sheet,
                        width=500,
                        style=ButtonStyle(
                            text_style=TextStyle(
                                size=18, weight=FontWeight.BOLD, color="green"
                            )
                        ),
                    ),
                    TextButton(
                        "إلغاء",
                        width=500,
                        style=ButtonStyle(
                            text_style=TextStyle(
                                size=18, weight=FontWeight.BOLD, color="green"
                            )
                        ),
                        on_click=lambda e: close(alert),
                    ),
                ],
            )
        ],
    )

    alert2 = AlertDialog(
        title=Text(
            "إضافة جهاز جديد",
            text_align=TextAlign.RIGHT,
        ),
        adaptive=True,
        content_padding=20,
        actions_alignment="center",
        modal=True,
        shape=RoundedRectangleBorder(radius=10),
        actions=[
            Column(
                spacing=10,
                controls=[
                    TextButton(
                        "موافق",
                        on_click=lambda e: [
                            reload_devicetype(
                                script.add_new_device(new_device_input.value)
                            ),
                            close(alert2),
                            page.update(),
                        ],
                        width=500,
                        style=ButtonStyle(
                            text_style=TextStyle(
                                size=18, weight=FontWeight.BOLD, color="green"
                            )
                        ),
                    ),
                    TextButton(
                        "إلغاء",
                        width=500,
                        style=ButtonStyle(
                            text_style=TextStyle(
                                size=18, weight=FontWeight.BOLD, color="green"
                            )
                        ),
                        on_click=lambda e: close(alert2),
                    ),
                ],
            )
        ],
    )

    device = Row(
        [
            Container(Icon(Icons.PERM_DEVICE_INFO, color=Colors.YELLOW_900), 7),
            Container(
                device_dropdown,
                expand=True,
            ),
            Container(IconButton(icon=Icons.ADD, on_click=show_new_total_dialog2)),
        ],
    )

    price_input = TextField(
        label="الـــــســـــعـــــر",
        text_align=TextAlign.RIGHT,
        text_size=20,
        text_style=TextStyle(font_family="Franklin Gothic"),
        keyboard_type=KeyboardType(KeyboardType.NUMBER),
        icon=Icon(Icons.ATTACH_MONEY_OUTLINED, color=Colors.GREEN_400, size=30),
        color=Colors.BLACK,
        label_style=TextStyle(
            color=Colors.BLACK, weight=FontWeight.BOLD, font_family="Arial", size=25
        ),
    )

    sales_input = TextField(
        label="الـــــمـــــبـــــاع",
        text_align=TextAlign.RIGHT,
        text_size=20,
        text_style=TextStyle(font_family="Franklin Gothic"),
        icon=Icon(Icons.ONETWOTHREE, color=Colors.BLACK87, size=30),
        keyboard_type=KeyboardType(KeyboardType.NUMBER),
        color=Colors.BLACK,
        label_style=TextStyle(
            color=Colors.BLACK, weight=FontWeight.BOLD, font_family="Arial", size=25
        ),
    )

    stats_row1 = Row(
        controls=[
            create_stat_card(
                "العدد الكلي", script.show(state.cust, device_dropdown.value)[0]
            ),
            create_stat_card(
                "اجمالي المبيعات", script.show(state.cust, device_dropdown.value)[1]
            ),
        ],
        alignment=MainAxisAlignment.SPACE_BETWEEN,
    )

    stats_row2 = Row(
        controls=[
            create_stat_card(
                "العدد الحالي", script.show(state.cust, device_dropdown.value)[2]
            ),
            create_stat_card(
                "اجمالي السعر", f"$ {script.show(state.cust, device_dropdown.value)[3]}"
            ),
        ],
        alignment=MainAxisAlignment.SPACE_BETWEEN,
    )

    mahmoud_button = ElevatedButton(
        "مــحــمــود",
        width=BUTTON_WIDTH - 10,
        height=BUTTON_HEIGHT,
        bgcolor=Colors.GREEN_ACCENT_700 if state.cust == "محمود" else BG_COLOR,
        color=Colors.BLACK,
        style=ButtonStyle(
            shape=RoundedRectangleBorder(BUTTON_BORDER_RADIUS),
            overlay_color=Colors.AMBER_100,
            surface_tint_color=Colors.RED,
            shadow_color=Colors.BLACK,
            text_style=TextStyle(
                color=Colors.BLACK,
                weight=FontWeight.BOLD,
                size=BUTTON_TEXT_SIZE,
                font_family=BUTTON_FONT_FAMILY,
            ),
        ),
        on_click=lambda e: [
            setattr(state, "index", 0),
            setattr(state, "cust", "محمود"),
            update_stats(e),
            setattr(sales_input, "value", ""),
            setattr(price_input, "value", ""),
            update_table(),
            update_cust(e),
            page.update(),
        ],
    )

    ashraf_button = ElevatedButton(
        "أشـــــــرف",
        width=BUTTON_WIDTH,
        height=BUTTON_HEIGHT,
        bgcolor=Colors.GREEN_ACCENT_700 if state.cust == "اشرف" else BG_COLOR,
        color=Colors.BLACK,
        style=ButtonStyle(
            shape=RoundedRectangleBorder(BUTTON_BORDER_RADIUS),
            shadow_color=Colors.BLACK,
            overlay_color=Colors.AMBER_100,
            surface_tint_color=Colors.RED,
            text_style=TextStyle(
                color=Colors.BLACK,
                weight=FontWeight.BOLD,
                size=BUTTON_TEXT_SIZE,
                font_family=BUTTON_FONT_FAMILY,
            ),
        ),
        on_click=lambda e: [
            setattr(state, "index", 0),
            setattr(state, "cust", "اشرف"),
            update_stats(e),
            setattr(sales_input, "value", ""),
            setattr(price_input, "value", ""),
            update_table(),
            update_cust(e),
            page.update(),
        ],
    )

    top_buttons = Row(
        controls=[
            ashraf_button,
            mahmoud_button,
        ],
        alignment=MainAxisAlignment.SPACE_BETWEEN,
    )

    add_button = ElevatedButton(
        "اضــــــافــــــــــــة",
        width=page.window.width,
        color=Colors.WHITE,
        bgcolor=Colors.GREEN_600,
        icon=Icons.ADD,
        style=ButtonStyle(
            text_style=TextStyle(23, weight=FontWeight.BOLD), icon_size=30
        ),
        on_click=lambda e: [
            script.add(
                state.cust,
                device_dropdown.value,
                sales_input.value.strip(),
                price_input.value.strip(),
            ),
            [
                setattr(sales_input, "value", ""),
                setattr(price_input, "value", ""),
                update_stats(e),
                page.update(),
            ],
            page.update(),
        ],
    )

    close_button = ElevatedButton(
        "اضافه / انهاء الشيت",
        width=page.window.width,
        bgcolor=Colors.RED_400,
        color=Colors.WHITE,
        icon=Icons.CLOSE,
        style=ButtonStyle(text_style=TextStyle(23), icon_size=30),
        on_click=show_new_total_dialog,
    )

    def table(table_number=0):
        data = script.get_data(state.cust, device_dropdown.value, table_number)
        return DataTable(
            columns=[
                DataColumn(Text("السعر", size=20)),
                DataColumn(Text("المباع", size=20)),
                DataColumn(Text("التاريخ", size=20)),
            ],
            rows=[
                DataRow(
                    cells=[
                        DataCell(
                            Text(
                                f"{row[0]:,}",
                                color=Colors.BLACK if row[0] >= 0 else Colors.RED,
                            )
                        ),
                        DataCell(
                            Text(
                                row[1],
                                color=Colors.BLACK if row[1] >= 0 else Colors.RED,
                            )
                        ),
                        DataCell(Text(row[2])),
                    ]
                )
                for row in data
            ]
            + [
                DataRow(
                    cells=[
                        DataCell(
                            Text(
                                c,
                                color=Colors.DEEP_PURPLE_ACCENT_700,
                                size=20,
                                weight=FontWeight.BOLD,
                            )
                        ),
                        DataCell(
                            Text(
                                c,
                                color=Colors.DEEP_PURPLE_ACCENT_700,
                                size=20,
                                weight=FontWeight.BOLD,
                            )
                        ),
                        DataCell(Text()),
                    ]
                )
                for c in script.show(state.cust, device_dropdown.value)
            ],
            data_row_max_height=50,
            data_row_min_height=50,
            data_text_style=TextStyle(size=20),
            width=page.window.width,
        )

    tabs = Tabs(
        selected_index=max(
            0, script.larged_table(state.cust, device_dropdown.value) - 1
        ),
        animation_duration=400,
        indicator_color=Colors.BLUE_ACCENT,
        height=60
        * len(
            script.get_data(
                state.cust,
                device_dropdown.value,
                script.larged_table(state.cust, device_dropdown.value),
            )
        )
        + 60,
        tabs=[
            Tab(
                text=str(i),
                content=table(i),
                height=50,
            )
            for i in script.get_tables(state.cust, device_dropdown.value)
        ],
        on_change=update_tabs,
        scrollable=True,
        label_text_style=TextStyle(size=20),
    )

    page.add(
        SafeArea(top_buttons),
        device,
        Divider(height=10),
        price_input,
        sales_input,
        add_button,
        Divider(height=10),
        stats_row1,
        stats_row2,
        Divider(height=10),
        close_button,
        Divider(),
        tabs,
    )
    update_height(0)


app(main)
