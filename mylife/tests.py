from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from mylife.models import Event, EventType, Location


class EventAdminMapTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username='map-admin', password='test-password',
        )
        event_type = EventType.objects.create(name='Trip')
        location = Location.objects.create(lat=0, lng=0)
        for name, notes in [('First', '</script><script>alert(1)</script>'),
                            ('Second', 'Another visit')]:
            Event.objects.create(name=name, notes=notes, location=location,
                                 event_type=event_type, event_time=timezone.now())
        Event.objects.create(
            name='Missing GPS', location=Location.objects.create(lat=10),
            event_type=event_type, event_time=timezone.now(),
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_map_referrer_policy_survives_security_middleware(self):
        response = self.client.get(reverse('admin:mylife_event_changelist'))
        self.assertEqual(
            response.headers['Referrer-Policy'], 'strict-origin-when-cross-origin',
        )
        other_page = self.client.get(reverse('admin:index'))
        self.assertEqual(other_page.headers['Referrer-Policy'], 'same-origin')

    def test_map_groups_shared_coordinates_and_escapes_notes(self):
        response = self.client.get(reverse('admin:mylife_event_changelist'))
        self.assertTemplateUsed(response, 'admin/mylife/event/change_list.html')
        figure = response.context['event_map']
        bounds = figure['layout']['map']['bounds']
        self.assertLess(bounds['east'] - bounds['west'], 360)
        self.assertLess(bounds['west'], bounds['east'])
        trace = figure['data'][0]
        self.assertEqual(trace['lat'], [0])
        self.assertEqual(trace['lon'], [0])
        self.assertIn('First', trace['text'][0])
        self.assertIn('Second', trace['text'][0])
        self.assertIn('&lt;script&gt;', trace['text'][0])
        self.assertNotContains(response, '</script><script>alert(1)</script>')

    def test_map_uses_filtered_queryset(self):
        response = self.client.get(
            reverse('admin:mylife_event_changelist'), {'q': 'Second'},
        )
        text = response.context['event_map']['data'][0]['text'][0]
        self.assertIn('Second', text)
        self.assertNotIn('First', text)

    def test_map_without_coordinates_has_empty_state(self):
        response = self.client.get(
            reverse('admin:mylife_event_changelist'), {'q': 'Missing'},
        )
        self.assertIsNone(response.context['event_map'])
        self.assertContains(response, 'No events with valid GPS coordinates')
