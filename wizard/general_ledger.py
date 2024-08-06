# -*- coding: utf-8 -*-
from odoo import api, fields, models
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from io import BytesIO
import base64
from collections import defaultdict


class GeneralLedger(models.TransientModel):
    _name = 'general.ledger'
    _description = 'General Ledger'

    # Definición de campos para el modelo
    report_from_date = fields.Date(string="Reporte desde", required=True, default=fields.Date.context_today)
    report_to_date = fields.Date(string="Reporte hasta", required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
    file_content = fields.Binary(string="Archivo Contenido")
    file_name = fields.Char(string="Nombre del Archivo", default="Libro Mayor.xlsx")

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

        # Filtrar grupos de cuentas por prefijo
        group_model = self.env['account.group']
        groups = group_model.search([('major_account', '=', True)])

        row_index = 7  # Fila de inicio para los datos

        for group in groups:
            account_prefix = group.code_prefix_start
            accounts = self.env['account.account'].search([('code', 'like', f'{account_prefix}%')])

            # Obtener movimientos contables para las cuentas filtradas en el rango de fechas
            moves = self.env['account.move.line'].search([
                ('account_id', 'in', accounts.ids),
                ('date', '>=', self.report_from_date),
                ('date', '<=', self.report_to_date)
            ])

            # Calcular saldos iniciales consolidados para el grupo de cuentas
            initial_debit = 0.0
            initial_credit = 0.0
            initial_balance = 0.0
            for account in accounts:
                initial_moves = self.env['account.move.line'].search([
                    ('account_id', '=', account.id),
                    ('date', '<', self.report_from_date)
                ])
                for move in initial_moves:
                    initial_debit += move.debit
                    initial_credit += move.credit
                    initial_balance += move.debit - move.credit

            # Agrupar movimientos por fecha
            date_summaries = defaultdict(lambda: {'debit': 0.0, 'credit': 0.0})

            for move in moves:
                date_summaries[move.date]['debit'] += move.debit
                date_summaries[move.date]['credit'] += move.credit

            # Calcular totales para el grupo
            total_debit = sum(move.debit for move in moves)
            total_credit = sum(move.credit for move in moves)
            total_balance = total_debit - total_credit

            # Agregar datos del grupo en la fila 7
            ws.cell(row=row_index, column=1, value=account_prefix).font = bold_font
            ws.cell(row=row_index, column=2, value=group.name).font = bold_font
            ws.cell(row=row_index, column=4, value=total_debit).font = bold_font
            ws.cell(row=row_index, column=5, value=total_credit).font = bold_font
            ws.cell(row=row_index, column=6, value=total_balance).font = bold_font

            row_index += 1

            # Agregar la fila de saldo inicial para Debe, Haber, y Saldo
            ws.append([
                '',  # Código de cuenta en blanco
                'SALDO INICIAL',  # Etiqueta para el saldo inicial
                '', '', '',  # Celdas vacías para fecha y código de cuenta
                initial_debit,  # Saldo inicial Debe
                initial_credit,  # Saldo inicial Haber
                initial_balance  # Saldo inicial Saldo
            ])

            # Aplicar formato en negrita a toda la fila de saldo inicial
            for cell in ws[row_index]:
                cell.font = bold_font
            row_index += 1

            # Agregar los datos agrupados por fecha
            accumulated_debit = initial_debit
            accumulated_credit = initial_credit
            accumulated_balance = initial_balance

            for date, summary in date_summaries.items():
                accumulated_debit += summary['debit']
                accumulated_credit += summary['credit']
                accumulated_balance = accumulated_debit - accumulated_credit

                ws.append([
                    "",  # Código de cuenta en blanco
                    "Movimiento del",  # Reemplazado por "Movimiento del"
                    date,
                    summary['debit'],
                    summary['credit'],
                    summary['debit'] - summary['credit']
                ])
                row_index += 1

            # Agregar la fila de suma para cada grupo de cuentas
            ws.append([
                '',  # Código de cuenta en blanco
                'SUMA',  # Etiqueta para la suma
                '', '', '',  # Celdas vacías para fecha y código de cuenta
                accumulated_debit,  # Total acumulado Debe
                accumulated_credit,  # Total acumulado Haber
                accumulated_balance  # Total acumulado Saldo
            ])

            # Aplicar formato en negrita a toda la fila de suma
            for cell in ws[row_index]:
                cell.font = bold_font
            row_index += 1

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
