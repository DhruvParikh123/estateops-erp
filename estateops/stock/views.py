from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from projects.views import get_project_or_deny

from .forms import StockItemForm, StockUsageForm
from .models import StockItem, StockUsage


@login_required
def stock_list(request, project_id):
    project = get_project_or_deny(request, project_id)
    items = StockItem.objects.filter(project=project)
    usages = StockUsage.objects.filter(project=project)
    
    form = StockItemForm()
    usage_form = StockUsageForm(project=project)
    
    context = {
        "project": project,
        "items": items,
        "usages": usages,
        "form": form,
        "usage_form": usage_form,
        "can_manage": request.user.is_authenticated and request.user.is_admin_role,
    }
    return render(request, "stock/stock_list.html", context)


@login_required
def stock_create(request, project_id):
    project = get_project_or_deny(request, project_id)
    if not request.user.is_admin_role:
        messages.error(request, "Only admins can add new items.")
        return redirect("stock:list", project_id=project.id)

    if request.method == "POST":
        form = StockItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.project = project
            item.save()
            messages.success(request, "Item added to godown stock.")
            return redirect("stock:list", project_id=project.id)
        messages.error(request, "Please fix the errors and try again.")
    return redirect("stock:list", project_id=project.id)


@login_required
def stock_delete(request, project_id, pk):
    project = get_project_or_deny(request, project_id)
    if not request.user.is_admin_role:
        messages.error(request, "Only admins can remove items.")
        return redirect("stock:list", project_id=project.id)

    item = get_object_or_404(StockItem, pk=pk, project=project)
    item.delete()
    messages.success(request, "Item removed.")
    return redirect("stock:list", project_id=project.id)


@login_required
def stock_usage_create(request, project_id):
    project = get_project_or_deny(request, project_id)
    if not request.user.is_admin_role:
        messages.error(request, "Only admins can record stock usage.")
        return redirect("stock:list", project_id=project.id)

    if request.method == "POST":
        form = StockUsageForm(request.POST, project=project)
        if form.is_valid():
            usage = form.save(commit=False)
            stock_item = usage.stock_item
            
            # Verify sufficient stock
            if usage.quantity_used > stock_item.available:
                messages.error(
                    request, 
                    f"Insufficient stock for '{stock_item.item}'. Available: {stock_item.available}, Requested: {usage.quantity_used}."
                )
            else:
                # Deduct stock
                stock_item.available -= usage.quantity_used
                stock_item.save()
                
                # Save usage log
                usage.project = project
                usage.created_by = request.user
                usage.save()
                
                messages.success(
                    request, 
                    f"Logged usage of {usage.quantity_used} units for '{stock_item.item}'."
                )
            return redirect("stock:list", project_id=project.id)
        messages.error(request, "Failed to log stock usage. Please check inputs.")
    return redirect("stock:list", project_id=project.id)
