from pprint import pprint
import pymssql

# Delete order: 
# TbAgreementsApplied Id_Billing
# TbPaymentsApplied Id_Billing
# TbTaxesApplied Id_Billing
# TbBillingItem Id_Billing
# TbBillNovelty Id_Billing
# TbBilling Id_Billing
# TbTransactionValues Id_Transaction
# TbTransaction Id_Transaction


query = "SELECT COUNT(IdInvoice) as repetidas, IdInvoice, Id_Device, InvoiceDate, (SELECT TOP 1 b.LastInsert FROM Tb_Billing b WHERE b.Id_Device = bill.Id_Device AND b.IdInvoice = bill.IdInvoice AND b.InvoiceDate = bill.InvoiceDate ORDER BY LastInsert asc) as FirstDate FROM Tb_Billing bill WHERE IdInvoice != 0 GROUP BY IdInvoice, Id_Device, InvoiceDate HAVING COUNT(IdInvoice)>1 ORDER BY repetidas asc"

queryDelete = "DELETE FROM Tb_Billing WHERE IdInvoice = %s AND Id_Device = %s AND InvoiceDate = %s AND LastInsert > %s ON CASCADE"

def deleteTransactions():
    conn = pymssql.connect(server='localhost', user='ci24', password='jupiter2040', database='Ci_ControlAccessDb')
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    transactions = {}
    for row in rows:
        vecesRepetida = row[0]
        idInvoice = row[1]
        idDevice = row[2]
        invoiceDate = row[3]
        firstDate = row[4]
        transactions[idInvoice]={'idDevice':idDevice, 'invoiceDate':invoiceDate, 'firstDate':firstDate, 'vecesRepetida':vecesRepetida, 'vecesEliminada':0, 'vecesNoEliminada':0,
        'agreementsDeleted':0, 'paymentsDeleted':0, 'taxesDeleted':0, 'itemsDeleted':0, 'noveltiesDeleted':0, 'billingDeleted':0, 'transactionValuesDeleted':0, 'transactionsDeleted':0}
    
    for transaction in transactions:
        billingsToDelete = []
        
        cursor.execute("SELECT Id_Billing, Id_Transaction FROM Tb_Billing WHERE IdInvoice = %s AND Id_Device = %s AND InvoiceDate = %s AND LastInsert > %s", (transaction, transactions[transaction]['idDevice'], transactions[transaction]['invoiceDate'], transactions[transaction]['firstDate']))
        
        for row in cursor.fetchall():
            billingsToDelete.append({"idBilling":row[0], "idTransaction":row[1]})
            cursor.execute("DELETE FROM Tb_AgreementsApplied WHERE Id_Billing = %s", row[0])
            transactions[transaction]['agreementsDeleted'] += cursor.rowcount
            cursor.execute("DELETE FROM Tb_PaymentsApplied WHERE Id_Billing = %s", row[0])
            transactions[transaction]['paymentsDeleted'] += cursor.rowcount
            cursor.execute("DELETE FROM Tb_TaxesApplied WHERE Id_Billing = %s", row[0])
            transactions[transaction]['taxesDeleted'] += cursor.rowcount
            cursor.execute("DELETE FROM Tb_BillingItem WHERE Id_Billing = %s", row[0])
            transactions[transaction]['itemsDeleted'] += cursor.rowcount
            cursor.execute("DELETE FROM Tb_BillNovelty WHERE Id_Billing = %s", row[0])
            transactions[transaction]['noveltiesDeleted'] += cursor.rowcount
            cursor.execute("DELETE FROM Tb_Billing WHERE Id_Billing = %s", row[0])
            transactions[transaction]['billingDeleted'] += cursor.rowcount
            cursor.execute("DELETE FROM Tb_TransactionValues WHERE Id_Transaction = %s", row[1])
            transactions[transaction]['transactionValuesDeleted'] += cursor.rowcount
            cursor.execute("DELETE FROM Tb_Transaction WHERE Id_Transaction = %s", row[1])
            transactions[transaction]['transactionsDeleted'] += cursor.rowcount
            
        
        
        #cursor.execute(queryDelete, (transaction, transactions[transaction]['idDevice'], transactions[transaction]['invoiceDate'], transactions[transaction]['firstDate']))
        cursor.execute("SELECT * FROM Tb_Billing WHERE IdInvoice = %s AND Id_Device = %s", (transaction, transactions[transaction]['idDevice']))
        transactions[transaction]['vecesNoEliminada'] = len(cursor.fetchall())
    
    conn.commit()
    conn.close()
    
    return transactions

results = deleteTransactions()

#open results.txt
f = open('results.txt', 'w')
for invoice in results:
    f.write("Invoice: " + str(invoice) + "\n")
    f.write("==============================\n")
    f.write("IdDevice: " + str(results[invoice]['idDevice']) + "\n")
    f.write("InvoiceDate: " + str(results[invoice]['invoiceDate']) + "\n")
    f.write("FirstDate: " + str(results[invoice]['firstDate']) + "\n")
    f.write("VecesRepetida: " + str(results[invoice]['vecesRepetida']) + "\n")
    f.write("VecesEliminada: " + str(results[invoice]['vecesEliminada']) + "\n")
    f.write("VecesNoEliminada: " + str(results[invoice]['vecesNoEliminada']) + "\n")
    f.write("AgreementsDeleted: " + str(results[invoice]['agreementsDeleted']) + "\n")
    f.write("PaymentsDeleted: " + str(results[invoice]['paymentsDeleted']) + "\n")
    f.write("TaxesDeleted: " + str(results[invoice]['taxesDeleted']) + "\n")
    f.write("ItemsDeleted: " + str(results[invoice]['itemsDeleted']) + "\n")
    f.write("NoveltiesDeleted: " + str(results[invoice]['noveltiesDeleted']) + "\n")
    f.write("BillingDeleted: " + str(results[invoice]['billingDeleted']) + "\n")
    f.write("TransactionValuesDeleted: " + str(results[invoice]['transactionValuesDeleted']) + "\n")
    f.write("TransactionsDeleted: " + str(results[invoice]['transactionsDeleted']) + "\n")
    f.write("==============================\n")
f.close()