from gsalud.models import ReceiptType, RecordType


def get_receipt_by_short(receipt_short):
    try:
        try: 
            return ReceiptType.objects.get(receipt_short=receipt_short)
        except ReceiptType.DoesNotExist:
            new_receipt = ReceiptType(
                    receipt_short = receipt_short,
                    receipt_text = receipt_short)
            new_receipt.save()
            return new_receipt
    except Exception as e:
        print(e)
        return False, str(e)


# --------- RecordTypes ----------


def get_record_type_by_name(type_name):
    try:
        try: 
            return RecordType.objects.get(record_name=type_name)
        except RecordType.DoesNotExist:
            new_type = RecordType(
                    record_name = type_name,
                    record_desc = type_name)
            new_type.save()
            return new_type
    except Exception as e:
        print(e)
        return False, str(e)
