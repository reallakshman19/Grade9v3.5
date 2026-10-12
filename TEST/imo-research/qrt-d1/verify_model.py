"""Independent integer group-model oracle for the AUTHORED MODEL-D1 TEST."""
def group_total(n:int,k:int)->int:
    assert type(n)==type(k)==int and n>0 and k>0
    return n*k
def recover_groups(total:int,k:int)->int:
    assert total>0 and k>0 and total%k==0
    return total//k
def verify():
    assert group_total(3,5)==15
    assert group_total(6,4)==24
    assert group_total(4,2)==8
    assert group_total(2,1)==2
    assert group_total(5,2)==10
    assert recover_groups(24,4)==6
    count=0
    for n in range(1,26):
        for k in range(1,26):
            total=group_total(n,k)
            assert total==sum([k]*n)
            assert recover_groups(total,k)==n
            count+=1
    print(f"MODEL-D1: {count} equal-group construction/inverse pairs and 6 boundary fixtures PASS")
if __name__=="__main__":verify()
