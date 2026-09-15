## 2. Facturation depuis la France

Deux régimes coexistent, et ils ne produisent pas le même débit pour le même
prix affiché.

**Plateformes facturant en dollars via Stripe.** Un particulier français se voit
appliquer la TVA de 20 % au paiement : un forfait affiché à 20 $ donne lieu à un
débit de 24 $. Un professionnel qui renseigne son numéro de TVA
intracommunautaire bascule en autoliquidation : la facture est émise à 0 % de TVA
et le montant débité est strictement le montant hors taxes.

**Plateformes affichant un prix en euros TTC.** Le prix européen intègre déjà la
TVA. Le professionnel ne bénéficie alors d'aucune autoliquidation sur ce canal.

Les colonnes « € HT » et « € TTC » des tableaux qui suivent sont **calculées**,
jamais saisies : elles dérivent d'un taux de change unique et d'un taux de TVA
uniques, déclarés dans `catalog/_meta.yaml`. Quand le taux bouge, tout le
document suit.

Un point de vigilance qui coûte cher en pratique : **ne pas confondre un
abonnement de chat grand public avec une consommation d'API**. Les deux
s'expriment en dollars par mois mais ne financent pas la même chose, et seul le
second passe à l'échelle d'une équipe.
