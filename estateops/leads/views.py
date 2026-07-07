from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from projects.views import get_project_or_deny

from .forms import FollowUpForm, LeadForm
from .models import Lead


@login_required
def lead_list(request, project_id):
    project = get_project_or_deny(request, project_id)
    tab = request.GET.get("tab", "active")
    leads = Lead.objects.filter(project=project)

    if tab == "active":
        leads = leads.filter(status=Lead.Status.ACTIVE)
    elif tab == "interested":
        leads = leads.filter(status=Lead.Status.INTERESTED)
    elif tab == "lost":
        leads = leads.filter(status=Lead.Status.LOST)

    lead_form = LeadForm()

    context = {
        "project": project,
        "leads": leads,
        "tab": tab,
        "lead_form": lead_form,
    }
    return render(request, "leads/lead_list.html", context)


@login_required
def lead_create(request, project_id):
    project = get_project_or_deny(request, project_id)
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.project = project
            lead.created_by = request.user
            lead.save()
            messages.success(request, f"Lead '{lead.client_name}' added.")
            return redirect("leads:list", project_id=project.id)
        messages.error(request, "Please fix the errors and try again.")
    return redirect("leads:list", project_id=project.id)


@login_required
def followup_create(request, project_id, pk):
    project = get_project_or_deny(request, project_id)
    lead = get_object_or_404(Lead, pk=pk, project=project)
    if request.method == "POST":
        form = FollowUpForm(request.POST)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.lead = lead
            followup.created_by = request.user
            followup.save()

            outcome_to_status = {
                "interested": Lead.Status.INTERESTED,
                "not_interested": Lead.Status.ACTIVE,
                "lost": Lead.Status.LOST,
                "converted": Lead.Status.CONVERTED,
                "no_response": lead.status,
            }
            
            new_status = outcome_to_status.get(followup.outcome, lead.status)
            
            if followup.outcome == "no_response":
                total_followups = lead.followups.count()
                if total_followups >= 3:
                    new_status = Lead.Status.LOST
                    messages.warning(request, f"Lead '{lead.client_name}' auto-marked as LOST due to 3 or more follow-ups ending in no response.")
            
            lead.status = new_status
            if followup.next_followup_date:
                lead.next_followup_date = followup.next_followup_date
            lead.save()
            messages.success(request, f"Follow-up saved for {lead.client_name}.")
        else:
            messages.error(request, "Please fix the errors and try again.")
    return redirect("leads:list", project_id=project.id)
