from django.db.models import Q, F, Case, When, BooleanField, Value
from gsalud.models import RecordInfo


def get_records_received():
    try:
        # Query using Django ORM
        base_queryset = RecordInfo.objects.annotate(
            record_key=F('id_record__record_key'),
            part_g_salud=F(
                'id_record__id_provider__id_particularity__part_g_salud'),
            part_prevencion=F(
                'id_record__id_provider__id_particularity__part_prevencion'),
            priority_case=Case(
                When(
                    Q(id_record__id_provider__priority=False),
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            ),
            id_provider=F('id_record__id_provider__id_provider'),
            business_name=F('id_record__id_provider__business_name'),
            id_coordinator=F('id_record__id_provider__id_coordinator'),
            record_total=F('id_record__record_total'),
            user_name=F('id_auditor__user_name'),
            particularity_mixed=Case(
                When(
                    Q(id_record__id_provider__id_particularity__part_prevencion__isnull=False) |
                    Q(id_record__id_provider__id_particularity__part_g_salud__isnull=False),
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        base_queryset = base_queryset.filter(
            Q(date_entry_digital__isnull=False) &
            Q(date_entry_physical__isnull=False) &
            Q(seal_number__isnull=False)
        )

        return base_queryset.values(
            'id_record', 'record_key', 'priority_case','id_provider', 'business_name',
            'id_coordinator', 'record_total','id_auditor', 'user_name','particularity_mixed',
            'date_assignment_audit', 'date_entry_digital','date_entry_physical', 
            'seal_number', 'observation'
        )
    except Exception as e:
        print(e)
        return None


reports = {
    '1': get_records_received
}
