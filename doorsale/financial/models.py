from __future__ import unicode_literals

from django.db import models


class Currency(models.Model):
    """
    Represents a currency
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True, help_text="ISO Currency Code")
    exchange_rate = models.FloatField(default=1.0)
    locale = models.CharField(max_length=10)
    display_format = models.CharField(max_length=50, help_text='Display format: 1.2 => "$%.2f" => $1.20 (python format string)')
    is_primary = models.BooleanField(default=False, help_text='Primary currency of site, you should updated exchange rate and product prices when you choose change primary currency')
    is_active = models.BooleanField(default=False)
    updated_by = models.CharField(max_length=100)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    
    class Meta:
        ordering = ('id',)
        verbose_name_plural = 'Currencies'
    
    def __unicode__(self):
        return self.name


class TaxRate(models.Model):
    """
    Represents a Tax Category
    """
    TAX_PERCENTAGE = 'PE'
    TAX_FIXED = 'FI'
    TAX_METHODS = ((TAX_PERCENTAGE, 'Percentage'),
                   (TAX_FIXED, 'Fixed'))
    
    name = models.CharField(max_length=100, unique=True)
    method = models.CharField(max_length=2, choices=TAX_METHODS, help_text='Tax deduction method: fixed tax per product or percentage (in fraction) of price per product')
    rate = models.FloatField(default=0.0)
    updated_by = models.CharField(max_length=100)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'financial_tax_rate'
        verbose_name_plural = 'Tax Rates'
    
    def __unicode__(self):
        return '%s [%s]: %s' % (self.name, self.method, self.rate)
    
    def calculate(self, price, quantity):
        """
        Calculate tax on price & quantity based on tax method
        """
        self._calculate(price, quantity, self.method, self.rate, self.name) 
    
    @classmethod
    def get_taxes(cls):
        """
        Return all taxes defined in system
        """
        return list(cls.objects.all())
    
    @classmethod
    def _calculate(cls, price, quantity, method, rate, name=None):
        """
        Calculate tax on price & quantity based on tax method
        """
        if method == cls.TAX_FIXED:
            return rate * quantity
        elif method == cls.TAX_PERCENTAGE:
            return rate * quantity * price
        
        if name:
            raise Exception('Unknown tax method "%s" defined for tax rate: "%s"' % (method, name))
        
        raise Exception('Unknown tax method "%s"' % method)  