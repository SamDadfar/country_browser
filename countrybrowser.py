from countryApi.countryapi import RestCountryApi
from tkinter import *
import wget
import requests
from PIL import Image, ImageTk
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
import fnmatch
import os
from tkinter import ttk
from tkinter import messagebox

"""
Browse countries base on some filter option as region, subregion, language, calling code
capital city and ISO code
"""


class FilterFrame(LabelFrame):
    def __init__(self, parent):
        LabelFrame.__init__(self, parent, relief=SUNKEN, text="Filters", padx=10, pady=10, fg='blue', bg='light gray')
        self.parent = parent
        self.default_countries_name = self.parent.api.get_attr_countries("name")
        self.default_country = self.parent.api.get_countries_by_name(self.default_countries_name[0])[0]
        self.filter_widgets()

    def filter_widgets(self):
        global lbl_font, combo_font, filters
        # field combobox
        self.field_lbl = Label(self, text="Filtered Field", font=lbl_font, padx=10, pady=10, bg='light gray')
        self.field_lbl.grid(row=0, column=0)
        self.field_combo = ttk.Combobox(self, values=filters, font=combo_font)
        self.field_combo.current(0)
        self.field_combo.bind("<<ComboboxSelected>>", self.field_combo_click)
        self.field_combo.grid(row=0, column=1)
        # subfield combobox
        self.subfield_lbl = Label(self, text="Filtered SubField", font=lbl_font, padx=10, pady=10, bg='light gray')
        self.subfield_combo = ttk.Combobox(self, values=[], font=combo_font)
        self.subfield_combo.bind("<<ComboboxSelected>>", self.subfield_combo_click)
        # countries combobox
        self.country_lbl = Label(self, text="Country Name", font=lbl_font, padx=10, pady=10, bg='light gray')
        self.country_lbl.grid(row=1, column=0)
        self.countries_combo = ttk.Combobox(self, values=self.default_countries_name, font=combo_font)
        self.countries_combo.bind("<<ComboboxSelected>>", self.countries_combo_click)
        self.countries_combo.current(0)
        self.countries_combo.grid(row=1, column=1)

    def field_combo_click(self, event):
        """
        change layout filters frame base on user choice
        :param event: event object of field combobox
        :return: None
        """
        selected_field = event.widget.get()
        if selected_field == "Name":
            self.hide_subfield()
            self.update_countries(self.parent.api.get_all())
            self.parent.details.change_details(self.default_country)

        elif selected_field == "Region":
            self.show_subfield(self.parent.api.get_regions())
            selected_countries = self.parent.api.get_countries_by_region(self.subfield_combo.get())
            self.update_countries(selected_countries)
            selected_country = self.parent.api.get_countries_by_name(self.countries_combo.get())[0]
            self.parent.details.change_details(selected_country)

        elif selected_field == "Subregion":
            self.show_subfield(self.parent.api.get_subregions())
            selected_countries = self.parent.api.get_countries_by_subregion(self.subfield_combo.get())
            self.update_countries(selected_countries)
            selected_country = self.parent.api.get_countries_by_name(self.countries_combo.get())[0]
            self.parent.details.change_details(selected_country)

        elif selected_field == "ISO code":
            self.show_subfield(self.parent.api.get_attr_countries("alpha3_code"))
            selected_country = self.parent.api.get_country_by_country_code(self.subfield_combo.get())
            self.update_countries([selected_country])
            self.parent.details.change_details(selected_country)

        elif selected_field == "Calling code":
            self.show_subfield(self.parent.api.get_attr_countries("calling_codes"))
            selected_countries = self.parent.api.get_countries_by_calling_code(self.subfield_combo.get())
            self.update_countries(selected_countries)
            selected_country = self.parent.api.get_countries_by_name(self.countries_combo.get())[0]
            self.parent.details.change_details(selected_country)

        elif selected_field == "Language":
            lang_dic = self.parent.api.get_languages()
            lang_names = lang_dic["names"]
            lang_codes = lang_dic["codes"]
            self.show_subfield(lang_names)
            for i, name in enumerate(lang_names):
                if name == self.subfield_combo.get():
                    default_lang_iso = lang_codes[i]
                    selected_countries = self.parent.api.get_countries_by_language(default_lang_iso)
                    self.update_countries(selected_countries)
                    selected_country = self.parent.api.get_countries_by_name(self.countries_combo.get())[0]
                    self.parent.details.change_details(selected_country)
                    break
        elif selected_field == "Capital":
            self.show_subfield(self.parent.api.get_attr_countries("capital"))
            selected_countries = self.parent.api.get_countries_by_capital(self.subfield_combo.get())
            self.update_countries(selected_countries)
            selected_country = self.parent.api.get_countries_by_name(self.countries_combo.get())[0]
            self.parent.details.change_details(selected_country)

    def subfield_combo_click(self, event):
        """
        Change layout of filters frame base on user choice
        :param event: event object of subfield combobox
        :return: None
        """
        selected_value = event.widget.get()
        filtered_field = self.field_combo.get()

        if filtered_field == "Region":
            selected_countries = self.parent.api.get_countries_by_region(selected_value)
            self.update_countries(selected_countries)
            selected_country = self.parent.api.get_countries_by_name(self.countries_combo.get())[0]
            self.parent.details.change_details(selected_country)
        elif filtered_field == "Subregion":
            selected_countries = self.parent.api.get_countries_by_subregion(selected_value)
            self.update_countries(selected_countries)
            selected_country = self.parent.api.get_countries_by_name(self.countries_combo.get())[0]
            self.parent.details.change_details(selected_country)
        elif filtered_field == "ISO code":
            selected_country = self.parent.api.get_country_by_country_code(selected_value)
            self.update_countries([selected_country])
            self.parent.details.change_details(selected_country)
        elif filtered_field == "Calling code":
            selected_country = self.parent.api.get_countries_by_calling_code(selected_value)[0]
            self.update_countries([selected_country])
            self.parent.details.change_details(selected_country)
        elif filtered_field == "Language":
            lang_dic = self.parent.api.get_languages()
            for i, name in enumerate(lang_dic["names"]):
                if name == selected_value:
                    code = lang_dic["codes"][i]
                    selected_countries = self.parent.api.get_countries_by_language(code)
                    self.update_countries(selected_countries)
                    selected_country = self.parent.api.get_countries_by_name(self.countries_combo.get())[0]
                    self.parent.details.change_details(selected_country)
                    break
        elif filtered_field == "Capital":
            selected_country = self.parent.api.get_countries_by_capital(selected_value)[0]
            self.update_countries([selected_country])
            self.parent.details.change_details(selected_country)

    def countries_combo_click(self, event):
        """
        Interact with user choice on countries combobox
        :param event: event object of countries combobox
        :return: None
        """
        selected_value = event.widget.get()
        selected_country = self.parent.api.get_countries_by_name(selected_value)[0]
        self.parent.details.change_details(selected_country)

    def show_subfield(self, lst):
        """
        Visible subfield and update list of items
        :param lst: list of countries
        :return: None
        """
        self.subfield_lbl["text"] = self.field_combo.get()
        self.subfield_combo["values"] = lst
        self.subfield_combo.current(0)
        self.subfield_lbl.grid(row=1, column=0)
        self.subfield_combo.grid(row=1, column=1)

    def hide_subfield(self):
        """
        Invisible subfield combobox
        :return:None
        """
        self.subfield_combo.grid_forget()
        self.subfield_lbl.grid_forget()

    def update_countries(self, lst, **kwargs):
        """
        update list of countries combobox
        :param lst: list of countries
        :return: None
        """
        if len(lst) == 1:
            names = [lst[0].name]
            self.countries_combo["state"] = "disabled"
        else:
            self.countries_combo["state"] = "normal"
            names = self.parent.api.get_attr_countries("name", countries=lst)
        self.countries_combo["values"] = names
        current = 0
        if len(kwargs) != 0 and kwargs['selected_country'] is not None:
            for i, name in enumerate(names):
                if name == kwargs['selected_country'].name:
                    current = i
        self.countries_combo.current(0 if current == 0 else current)
        self.country_lbl.grid(row=2, column=0)
        self.countries_combo.grid(row=2, column=1)


# container of country's details
class DetailFrame(LabelFrame):
    def __init__(self, parent):
        LabelFrame.__init__(self, parent, relief=SUNKEN, text="Details", padx=10, pady=10, fg='blue', bg='light blue')
        self.parent = parent
        self.detail_widgets(self.parent.filters.default_country)

    # list of widgets inside details frame
    def detail_widgets(self, country):
        self.img = DetailFrame.load_flag_image(country)
        self.flag_img = ImageTk.PhotoImage(self.img)
        self.image_lbl = Label(self, image=self.flag_img, bg='light blue')
        self.flag_lbl = Label(self, text="flag :", width=20, anchor=NW, font=lbl_font, padx=2, bg='light blue')
        self.flag_lbl.grid(row=0, column=0, sticky=W)
        self.image_lbl.grid(row=0, column=1, sticky=W)
        self.render_country_details(self, country)

    def change_details(self, country):
        """
        Change values of country's details
        :param country: country object
        :return: None
        """
        self.clear_frame()
        self.render_country_details(self, country)

    @staticmethod
    def load_flag_image(country):
        """
        download, reformat, load an image file as flag image from country image attribute
        :param country: Country object
        :return: None
        """
        base_path = "images/images_flags/"
        if not os.path.isdir(os.path.join(base_path)):
            os.mkdir(os.path.join(base_path))
        iso_code = str(country.alpha3_code).lower()
        file_name = iso_code + ".png"
        flag_url = country.flag
        if not os.path.isfile(os.path.join(base_path, file_name)):
            wget.download(flag_url, base_path)
            for file in os.listdir(base_path):
                if fnmatch.fnmatch(file, iso_code + ".svg"):
                    file_png = file.split(".")[0] + ".png"
                    svg_image = svg2rlg(base_path + file)
                    renderPM.drawToFile(svg_image, base_path + file_png, fmt="PNG")
                    image = Image.open(base_path + file_png)
                    image.thumbnail((200, 200))
                    image.save(base_path + file_png)
                    os.remove(os.path.join(base_path, file))
                    return image
        else:
            for file in os.listdir(base_path):
                if fnmatch.fnmatch(file, iso_code + ".png"):
                    image = Image.open(base_path + file)
                    return image

    @staticmethod
    def render_country_details(parent, country):
        """
        update details inside details frame
        :param parent:parent container
        :param country:country object
        :return:
        """
        pairs = dict(country.__dict__.items())
        parent.img = DetailFrame.load_flag_image(country)
        parent.flag_img = ImageTk.PhotoImage(parent.img)
        parent.image_lbl.config(image=parent.flag_img)
        parent.flag_lbl.grid(row=0, column=0, sticky=W)
        parent.image_lbl.grid(row=0, column=1, sticky=W)
        del pairs["relevance"]
        del pairs["flag"]
        row = 1
        for pair in pairs.items():
            if pair[1] is not None and pair[0] != "top_level_domain":
                if type(pair[1]) == list or str:
                    if len(str(pair[1])) == 0:
                        continue
                row += 1
                parent.draw_attribute(pair, row)

    def border_click(self, event, var):
        """
        link to selected country
        :param event: event object
        :param var: ISO code of country
        :return: None
        """
        all_countries = self.parent.api.get_all()
        selected_country = self.parent.api.get_country_by_country_code(var)
        self.parent.filters.hide_subfield()
        self.parent.filters.field_combo.current(0)
        self.parent.filters.update_countries(all_countries, selected_country=selected_country)
        self.change_details(selected_country)

    def draw_attribute(self, item, row):
        """
        draw attribute of country object inside details frame
        :param item: attribute of country object
        :param row: number of row
        :return: None
        """
        field_lbl = Label(self, text=item[0] + " :", width=20, anchor=W, font=lbl_font, padx=2, bg='light blue')
        txt = ""
        links = []
        if item[0] == "borders" and len(item[1]) > 0:
            links_frame = Frame(self, bg='light blue')
            links_frame.grid(row=row, column=1, columnspan=1, sticky=W)
            for border in item[1]:
                link_btn = Button(links_frame, text=border, font=detail_font, bg='light blue', fg="blue")
                link_btn.bind("<Button-1>", lambda event, v=border: self.border_click(event, v))
                links.append(link_btn)
            field_lbl.grid(row=row, column=0, sticky=W)
            for column, link in enumerate(links):
                link.grid(row=0, column=column, sticky=W, padx=2)
        else:
            if type(item[1]) == list and len(item[1]) != 0 and type(item[1][0]) != dict:
                for i, var in enumerate(item[1]):
                    txt += str(var)
                    txt += ", " if len(item[1]) != i + 1 else ""
            elif type(item[1]) == dict:
                txt = ""
                value = "{} = {}"
                for i, var in enumerate(item[1], start=1):
                    txt += str(value.format(var, item[1][var]))
                    if len(item[1]) != i:
                        txt += ", "
                    if len(item[1]) != i and i % 4 == 0:
                        txt += "\n"
            elif type(item[1]) == list and len(item[1]) != 0 and type(item[1][0]) == dict:
                for i, dic in enumerate(item[1], start=1):
                    dic_all = ""
                    for var in dic.items():
                        dic_all += str(var) + " "
                    txt += str(dic_all)
                    if len(item[1]) > 1 and len(item[1]) != i:
                        txt += "\n"
            else:
                if type(item[1]) != list:
                    txt = str(item[1])
            if len(txt) != 0:
                value_lbl = Label(self, text=txt, font=detail_font, bg='light blue')
                field_lbl.grid(row=row, column=0, sticky=W)
                value_lbl.grid(row=row, column=1, sticky=W)

    # clear all of widgets in details frame
    def clear_frame(self):
        """
        clear details frame
        :return:None
        """
        for widget in self.winfo_children():
            widget.grid_forget()


class MainWindow(Tk):
    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.parent = parent
        try:
            self.api = RestCountryApi()
            self.default_countries = self.api.get_all()
        except requests.exceptions.ConnectionError:
            self.popup = messagebox.showerror(title="No Internet Connection",
                                              message="You don't have any internet connection")
            if self.popup == 1:
                parent.quit()
        self.widgets()

    def widgets(self):
        self.filters = FilterFrame(self)
        self.filters.grid(row=0, column=0, padx=10, pady=10, sticky=N + S + E + W)
        self.details = DetailFrame(self)
        self.details.grid(row=1, column=0, padx=10, pady=10, sticky=N + S + E + W)


filters = ["Name", "Region", "Subregion", "ISO code", "Calling code", "Language", "Capital"]
lbl_font = ("Times", 10, "bold")
lbl_border_font = ("calibri", 12, "underline")
combo_font = ("courier", 10, "bold")
detail_font = ("calibri", 12)

if __name__ == '__main__':
    root = MainWindow(None)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.iconbitmap('images/maps.ico')
    root.title('Country Browser')
    root.geometry("{}x{}+0+0".format(screen_width, screen_height))
    root.mainloop()
