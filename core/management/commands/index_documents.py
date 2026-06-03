from django.core.management.base import BaseCommand
from core.models import CourseDocument
from core.services.assistant import index_document


class Command(BaseCommand):
    help = "Index all course documents into ChromaDB for RAG."

    def add_arguments(self, parser):
        parser.add_argument(
            "--course", type=int, default=None,
            help="Only index documents for this course ID."
        )

    def handle(self, *args, **options):
        qs = CourseDocument.objects.all()
        if options["course"]:
            qs = qs.filter(course_id=options["course"])

        total = qs.count()
        self.stdout.write(f"Indexing {total} document(s)...")

        for doc in qs:
            try:
                index_document(
                    course_id=doc.course_id,
                    document_id=doc.id,
                    file_path=doc.file.path,
                    title=doc.title,
                )
                self.stdout.write(self.style.SUCCESS(f"  [OK] {doc.title} (course {doc.course_id})"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [FAIL] {doc.title}: {e}"))

        self.stdout.write(self.style.SUCCESS("Done."))
