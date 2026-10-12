"""Independent original D1 SYNTHESIZE operation-order arithmetic oracle."""
def total(n,a,b):
 assert n>0 and a>=0 and b>=0 and a+b>0
 return n*(a+b)
def reverse(t,a,b):
 assert t>0 and a+b>0 and t%(a+b)==0
 return t//(a+b)
def verify():
 for n,a,b,t in [(3,2,1,9),(4,3,2,20),(2,4,2,12),(2,1,3,8),(4,1,2,12)]:
  assert total(n,a,b)==t and reverse(t,a,b)==n
 assert 3+2*4==11!=total(4,3,2)
 assert 4+2*2==8!=total(2,4,2)
 assert 1+3*2==7!=total(2,1,3)
 count=0
 for n in range(1,11):
  for a in range(0,12):
   for b in range(0,12):
    if a+b==0:continue
    t=total(n,a,b)
    assert t==n*a+n*b==sum([a+b]*n)
    assert reverse(t,a,b)==n
    count+=1
 print(f"SYNTHESIZE-D1: {count} independent mixed-unit/reversal checks plus 5 fixtures/3 counterexamples PASS")
if __name__=="__main__":verify()
