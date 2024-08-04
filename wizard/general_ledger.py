# -*- coding: utf-8 -*-
from odoo import api, fields, models
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from io import BytesIO
import base64

class GeneralLedger(models.TransientModel):
    _name = 'general.ledger'
    _description = 'General Ledger'

    # Definición de campos para el modelo
    report_from_date = fields.Date(string="Reporte desde", required=True, default=fields.Date.context_today)
    report_to_date = fields.Date(string="Reporte hasta", required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
    file_content = fields.Binary(string="Archivo Contenido")
    file_name = fields.Char(string="Nombre del Archivo", default="reporte.xlsx")

    def action_generate_excel(self):
        # Crear un libro de trabajo y una hoja
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"

        # Definir estilos
        bold_font = Font(bold=True)
        large_font = Font(size=14, bold=True)
        center_alignment = Alignment(horizontal='center')

        # Agregar el nombre de la compañía en mayúsculas, en negrita y centrado
        company_name = self.company_id.name.upper() if self.company_id else "NO DISPONIBLE"
        ws.merge_cells('A1:F1')  # Fusionar celdas de A1 a F1
        ws['A1'] = company_name
        ws['A1'].font = large_font
        ws['A1'].alignment = center_alignment

        # Agregar el título del reporte, en negrita y centrado
        report_title = f"LIBRO MAYOR CORRESPONDIENTE DEL {self.report_from_date} AL {self.report_to_date}"
        ws.merge_cells('A2:F2')  # Fusionar celdas de A2 a F2
        ws['A2'] = report_title
        ws['A2'].font = bold_font
        ws['A2'].alignment = center_alignment

        # Agregar el detalle de la moneda, centrado y en negrita
        currency_detail = "Expresado en: USD"
        ws.merge_cells('A3:F3')  # Fusionar celdas de A3 a F3
        cell = ws['A3']
        cell.value = currency_detail
        cell.font = bold_font  # Aplicar negrita
        cell.alignment = center_alignment

        # Agregar encabezados de la tabla
        headers = ['Codigo', 'Cuenta de mayor', 'Fecha', 'Debe', 'Haber', 'Saldo']
        ws.append(headers)
        for cell in ws[4]:  # Aplicar formato a los encabezados de la tabla
            cell.font = bold_font
            cell.alignment = center_alignment

        # Aquí puedes agregar lógica para recuperar datos basados en las fechas
        # Por simplicidad, añado datos estáticos como ejemplo
        data = [
            ['Dato1', 'Dato2', 'Dato3'],
            ['Dato4', 'Dato5', 'Dato6'],
        ]

        for row in data:
            ws.append(row)

        # Ajustar el ancho de las columnas
        for col_index, column in enumerate(ws.columns, start=1):
            max_length = 0
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            col_letter = chr(64 + col_index)  # Convertir el índice a letra de columna (A, B, C, ...)
            ws.column_dimensions[col_letter].width = adjusted_width

        # Guardar el archivo en memoria
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Codificar el archivo en base64
        file_content = base64.b64encode(output.read()).decode('utf-8')
        output.close()

        # Actualizar el campo `file_content` del wizard
        self.write({
            'file_content': file_content
        })

        # Crear un archivo adjunto en Odoo
        attachment = self.env['ir.attachment'].create({
            'name': self.file_name,
            'type': 'binary',
            'datas': file_content,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': 'general.ledger',
            'res_id': self.id
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'new',
        }
